"""Tela de produtos: cadastrar, editar, listar e excluir."""
import flet as ft

from componentes.alertas_ui import Sino
from componentes.ui import (abrir_dialogo, cabecalho, celula, fechar_dialogo,
                            painel, rolar_ao_topo, titulo_coluna)
from funcoes.alertas import invalidar_cache
from funcoes.produto import (atualizar_produto, buscar_produto,
                             deletar_produto, inserir_produto,
                             listar_produtos)
from tema import AZUL, AZUL_ESCURO, BRANCO, LINHA, TEXTO_SUAVE, VERDE, VERMELHO
from utils.datas import data_para_campo, formatar_data
from utils.erros import ErroValidacao, mensagem_amigavel, registrar_erro
from utils.validacao import validar_produto

# (chave, rótulo, largura). A chave é a mesma usada no banco e na validação.
CAMPOS = [
    ("nome", "Nome *", 260),
    ("categoria", "Categoria", 200),
    ("marca", "Marca", 200),
    ("codigo_barras", "Código de barras", 200),
    ("fornecedor", "Fornecedor", 240),
    ("preco_custo", "Preço de custo", 160),
    ("preco_venda", "Preço de venda *", 160),
    ("data_entrega", "Entrega * (dd/mm/aaaa)", 200),
    ("data_validade", "Validade * (dd/mm/aaaa)", 200),
    ("quantidade", "Quantidade *", 140),
    ("quantidade_minima", "Qtd. mínima", 140),
    ("lote", "Lote", 160),
    ("localizacao", "Localização", 200),
]

# Campos do dicionário devolvido por buscar_produto() que não têm o mesmo
# nome do campo da tela.
COLUNA_DO_CAMPO = {"quantidade": "quantidade_atual"}
CAMPOS_DE_DATA = ("data_entrega", "data_validade")
CAMPOS_DE_PRECO = ("preco_custo", "preco_venda")


def _texto_do_banco(chave, produto):
    """Converte um valor vindo do banco no texto que vai para o campo da tela."""
    valor = produto.get(COLUNA_DO_CAMPO.get(chave, chave))
    if valor is None:
        return ""
    if chave in CAMPOS_DE_DATA:
        return data_para_campo(valor)
    if chave in CAMPOS_DE_PRECO:
        return f"{valor:.2f}".replace(".", ",")
    return str(valor)


def criar_tela(page, navegar):
    campos = {chave: ft.TextField(label=rotulo, width=largura)
              for chave, rotulo, largura in CAMPOS}
    estado = {"id_em_edicao": None}  # None = modo cadastro
    sino = Sino(page, navegar)

    mensagem = ft.Text("", size=13)
    vazio = ft.Text(
        "Nenhum produto cadastrado ainda. Preencha o formulário e "
        "clique em Salvar produto.",
        color=TEXTO_SUAVE, size=13, visible=False,
    )
    titulo_form = ft.Text("Novo produto", size=16,
                          weight=ft.FontWeight.BOLD, color=AZUL_ESCURO)
    tabela = ft.DataTable(
        columns=[titulo_coluna(t) for t in
                 ["ID", "Produto", "Categoria", "Validade", "Quantidade",
                  "Local", "Ações"]],
        rows=[],
        column_spacing=28,
    )

    # ---------- mensagens e modos do formulário ----------

    def avisar(texto, erro=False):
        mensagem.value = texto
        mensagem.color = VERMELHO if erro else VERDE

    def tratar_erro(erro, contexto):
        """Mostra a mensagem amigável; erros inesperados vão para o log."""
        if not isinstance(erro, ErroValidacao):
            registrar_erro(erro, contexto)
        avisar(mensagem_amigavel(erro), erro=True)
        page.update()

    def atualizar_alertas():
        """Os dados mudaram: refaz a contagem do sino do cabeçalho."""
        invalidar_cache()
        sino.atualizar()

    def limpar_campos():
        for campo in campos.values():
            campo.value = ""

    def modo_cadastro():
        estado["id_em_edicao"] = None
        titulo_form.value = "Novo produto"
        btn_salvar.visible = True
        btn_limpar.visible = True
        btn_atualizar.visible = False
        btn_cancelar.visible = False

    def modo_edicao(id_produto):
        estado["id_em_edicao"] = id_produto
        titulo_form.value = f"Editar produto (ID {id_produto})"
        btn_salvar.visible = False
        btn_limpar.visible = False
        btn_atualizar.visible = True
        btn_cancelar.visible = True

    # ---------- tabela ----------

    def carregar_tabela():
        try:
            produtos = listar_produtos()
        except Exception as erro:
            registrar_erro(erro, "listar produtos")
            tabela.rows = []
            vazio.visible = False
            avisar(mensagem_amigavel(erro), erro=True)
            return

        def botoes(p):
            return ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=AZUL,
                        tooltip="Editar produto",
                        on_click=lambda e, i=p["id_produto"]: editar(i),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=VERMELHO,
                        tooltip="Excluir produto",
                        on_click=lambda e, i=p["id_produto"], n=p["nome"]:
                            pedir_exclusao(i, n),
                    ),
                ],
                spacing=0,
            )

        tabela.rows = [
            ft.DataRow(cells=[
                celula(p["id_produto"]),
                celula(p["nome"]),
                celula(p["categoria"] or "-"),
                celula(formatar_data(p["data_validade"])),
                celula(p["quantidade_atual"]),
                celula(p["localizacao"] or "-"),
                celula(botoes(p)),
            ])
            for p in produtos
        ]
        vazio.visible = not produtos

    # ---------- ações ----------

    def coletar_dados():
        valores = {chave: (campo.value or "").strip()
                   for chave, campo in campos.items()}
        return validar_produto(valores)

    def salvar(e):
        try:
            dados = coletar_dados()
            inserir_produto(**dados)
        except Exception as erro:
            tratar_erro(erro, "salvar produto")
            return
        limpar_campos()
        avisar(f"Produto '{dados['nome']}' salvo com sucesso.")
        atualizar_alertas()
        carregar_tabela()
        page.update()

    def editar(id_produto):
        try:
            produto = buscar_produto(id_produto)
        except Exception as erro:
            tratar_erro(erro, f"buscar produto {id_produto}")
            return
        if produto is None:
            avisar("Esse produto não existe mais (talvez já tenha sido "
                   "excluído).", erro=True)
            carregar_tabela()
            page.update()
            return
        for chave, campo in campos.items():
            campo.value = _texto_do_banco(chave, produto)
        modo_edicao(id_produto)
        avisar("")
        page.update()
        rolar_ao_topo(page, coluna_principal)

    def atualizar(e):
        id_produto = estado["id_em_edicao"]
        try:
            dados = coletar_dados()
            encontrado = atualizar_produto(id_produto, **dados)
        except Exception as erro:
            tratar_erro(erro, f"atualizar produto {id_produto}")
            return
        if not encontrado:
            avisar("Esse produto não existe mais; nada foi alterado.",
                   erro=True)
        else:
            avisar(f"Produto '{dados['nome']}' atualizado com sucesso.")
        limpar_campos()
        modo_cadastro()
        atualizar_alertas()
        carregar_tabela()
        page.update()

    def cancelar_edicao(e):
        limpar_campos()
        modo_cadastro()
        avisar("")
        page.update()

    def limpar(e):
        limpar_campos()
        avisar("")
        page.update()

    def pedir_exclusao(id_produto, nome):
        def confirmar(e):
            fechar_dialogo(page, dialogo)
            try:
                apagados = deletar_produto(id_produto)
            except Exception as erro:
                tratar_erro(erro, f"excluir produto {id_produto}")
                return
            if estado["id_em_edicao"] == id_produto:
                limpar_campos()
                modo_cadastro()
            if apagados:
                avisar(f"Produto '{nome}' excluído.")
            else:
                avisar("Esse produto já havia sido excluído.", erro=True)
            atualizar_alertas()
            carregar_tabela()
            page.update()

        def cancelar(e):
            fechar_dialogo(page, dialogo)

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir produto"),
            content=ft.Text(
                f"Deseja excluir '{nome}'? O estoque desse produto "
                "também será apagado."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.Button(
                    "Excluir produto",
                    on_click=confirmar,
                    style=ft.ButtonStyle(bgcolor=VERMELHO, color=BRANCO),
                ),
            ],
        )
        abrir_dialogo(page, dialogo)

    # ---------- botões (criados depois das funções que eles chamam) ----------

    btn_salvar = ft.Button(
        "Salvar produto", icon=ft.Icons.SAVE_OUTLINED, on_click=salvar,
        style=ft.ButtonStyle(bgcolor=AZUL, color=BRANCO))
    btn_limpar = ft.OutlinedButton("Limpar campos", on_click=limpar)
    btn_atualizar = ft.Button(
        "Salvar alterações", icon=ft.Icons.CHECK, on_click=atualizar,
        style=ft.ButtonStyle(bgcolor=AZUL, color=BRANCO), visible=False)
    btn_cancelar = ft.OutlinedButton(
        "Cancelar edição", on_click=cancelar_edicao, visible=False)

    carregar_tabela()

    coluna_principal = ft.Column(
        controls=[
            cabecalho("Produtos",
                      "Cadastre, consulte, edite e exclua os produtos do "
                      "mercado.", sino),
            ft.Divider(color=LINHA),
            ft.Container(
                bgcolor=BRANCO, padding=18, border_radius=12,
                content=ft.Column(
                    controls=[
                        titulo_form,
                        ft.Row(controls=list(campos.values()),
                               wrap=True, spacing=12, run_spacing=12),
                        ft.Row(
                            controls=[btn_salvar, btn_limpar,
                                      btn_atualizar, btn_cancelar],
                            spacing=10,
                        ),
                        mensagem,
                    ],
                    spacing=14,
                ),
            ),
            ft.Text("Produtos cadastrados", size=18,
                    weight=ft.FontWeight.BOLD, color=AZUL_ESCURO),
            painel(tabela),
            vazio,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    return coluna_principal
