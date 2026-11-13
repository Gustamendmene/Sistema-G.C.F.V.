import flet as ft
from datetime import datetime

from funcoes.produto import inserir_produto, deletar_produto, listar_produtos
from funcoes.estoque import (
    resumo_estoque,
    listar_alertas,
    listar_lotes,
    listar_estoque,
)

AZUL_ESCURO = "#123B70"
AZUL = "#2468AC"
BRANCO = "#FFFFFF"
CINZA = "#F4F6F9"
TEXTO_SUAVE = "#64748B"
VERMELHO = "#D94A4A"
AMARELO = "#D99B24"
LARANJA = "#E07B1F"
VERDE = "#2E9E5B"

CORES_ALERTA = {
    "VENCIDO": VERMELHO,
    "PRÓXIMO DO VENCIMENTO": AMARELO,
    "ESTOQUE BAIXO": LARANJA,
}


def converter_data(texto):
    """Converte 13/11/2026 para 2026-11-13 (formato que o MySQL entende)."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


def formatar_data(valor):
    """Mostra datas vindas do banco no formato dd/mm/aaaa."""
    if valor is None:
        return "-"
    try:
        return valor.strftime("%d/%m/%Y")
    except AttributeError:
        return str(valor)


def etiqueta(texto, cor):
    return ft.Container(
        content=ft.Text(texto, color=BRANCO, size=12,
                        weight=ft.FontWeight.BOLD),
        bgcolor=cor,
        padding=6,
        border_radius=6,
    )


def criar_cartao(titulo, valor, icone, cor):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icone, color=cor, size=28),
                ft.Text(titulo, size=13, color=TEXTO_SUAVE),
                ft.Text(str(valor), size=26, weight=ft.FontWeight.BOLD,
                        color=AZUL_ESCURO),
            ],
            spacing=8,
        ),
        bgcolor=BRANCO,
        padding=18,
        border_radius=12,
        expand=True,
    )


def montar_tabela(titulos, linhas):
    """Cria uma tabela só de leitura. Cada célula pode ser texto ou um controle."""
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(t, weight=ft.FontWeight.BOLD,
                                  color=AZUL_ESCURO))
            for t in titulos
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(c if isinstance(c, ft.Control)
                                else ft.Text(str(c)))
                    for c in linha
                ]
            )
            for linha in linhas
        ],
        column_spacing=28,
    )


def painel(tabela):
    """Caixa branca com rolagem horizontal para tabelas largas."""
    return ft.Container(
        content=ft.Row(controls=[tabela], scroll=ft.ScrollMode.AUTO),
        bgcolor=BRANCO,
        padding=12,
        border_radius=12,
    )


def abrir_dialogo(page, dialogo):
    if hasattr(page, "show_dialog"):
        page.show_dialog(dialogo)
    else:
        page.open(dialogo)


def fechar_dialogo(page, dialogo):
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        page.close(dialogo)

def linhas_lotes():
    return [
        (lote or "-", nome, formatar_data(validade), qtd, local or "-")
        for lote, nome, validade, qtd, local in listar_lotes()
    ]


def linhas_estoque():
    linhas = []
    for nome, qtd, minimo, atualizado in listar_estoque():
        if qtd <= minimo:
            situacao = etiqueta("ESTOQUE BAIXO", LARANJA)
        else:
            situacao = etiqueta("OK", VERDE)
        linhas.append((nome, qtd, minimo, situacao, formatar_data(atualizado)))
    return linhas


def linhas_validade():
    alertas = sorted(listar_alertas(), key=lambda linha: linha[3])
    linhas = []
    for id_p, nome, validade, dias, qtd, minimo, alerta in alertas:
        if dias < 0:
            prazo = f"venceu há {-dias} dia(s)"
        elif dias == 0:
            prazo = "vence hoje"
        else:
            prazo = f"{dias} dia(s)"
        linhas.append((
            id_p, nome, formatar_data(validade), prazo, qtd, minimo,
            etiqueta(alerta or "-", CORES_ALERTA.get(alerta, AZUL)),
        ))
    return linhas


def main(page: ft.Page):
    page.title = "Mercadinho São José"
    page.bgcolor = CINZA
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.min_width = 800
    page.window.min_height = 600

    area = ft.Container(expand=True, padding=28)
    botoes_menu = {}

    def mostrar(destino):
        """Troca a tela mostrada à direita e destaca o item do menu."""
        for chave, caixa in botoes_menu.items():
            caixa.bgcolor = AZUL if chave == destino else None
        area.content = telas[destino]()
        page.update()

    def item_menu(chave, icone, titulo):
        caixa = ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icone, color=BRANCO),
                title=ft.Text(titulo, color=BRANCO, size=14),
                on_click=lambda e: mostrar(chave),
            ),
            border_radius=8,
        )
        botoes_menu[chave] = caixa
        return caixa

    def cabecalho(titulo, subtitulo):
        return ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(titulo, size=25, weight=ft.FontWeight.BOLD,
                                color=AZUL_ESCURO),
                        ft.Text(subtitulo, color=TEXTO_SUAVE, size=13),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.NOTIFICATIONS_NONE,
                    icon_color=AZUL,
                    tooltip="Ver alertas de validade",
                    on_click=lambda e: mostrar("validade"),
                ),
            ],
        )

    def atalho(icone, titulo, descricao, destino):
        return ft.Container(
            bgcolor=BRANCO, padding=18, border_radius=12, ink=True,
            on_click=lambda e: mostrar(destino),
            content=ft.Row(
                controls=[
                    ft.Icon(icone, color=AZUL, size=30),
                    ft.Column(
                        controls=[
                            ft.Text(titulo, weight=ft.FontWeight.BOLD,
                                    color=AZUL_ESCURO),
                            ft.Text(descricao, size=12, color=TEXTO_SUAVE),
                        ],
                        spacing=3, expand=True,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD, color=AZUL),
                ],
            ),
        )

    def tela_inicio():
        aviso = ""
        try:
            produtos, lotes, proximos, vencidos = resumo_estoque()
        except Exception as erro:
            produtos = lotes = proximos = vencidos = 0
            aviso = ("Não foi possível ler o banco de dados. Confira se o "
                     f"MySQL está ligado e se o .env está correto. ({erro})")

        return ft.Column(
            controls=[
                cabecalho("Visão geral",
                          "Bem-vindo ao sistema do Mercadinho São José!"),
                ft.Divider(color="#DCE3EA"),
                ft.Text(aviso, color=VERMELHO, size=13, visible=bool(aviso)),
                ft.Text("Resumo do estoque", size=18,
                        weight=ft.FontWeight.BOLD, color=AZUL_ESCURO),
                ft.Row(
                    controls=[
                        criar_cartao("Produtos cadastrados", produtos,
                                     ft.Icons.INVENTORY_2_OUTLINED, AZUL),
                        criar_cartao("Lotes registrados", lotes,
                                     ft.Icons.LAYERS_OUTLINED, AZUL),
                    ],
                    spacing=14,
                ),
                ft.Row(
                    controls=[
                        criar_cartao("Próximos do vencimento", proximos,
                                     ft.Icons.ACCESS_TIME, AMARELO),
                        criar_cartao("Lotes vencidos", vencidos,
                                     ft.Icons.WARNING_AMBER_OUTLINED,
                                     VERMELHO),
                    ],
                    spacing=14,
                ),
                ft.Text("Acesso rápido", size=18,
                        weight=ft.FontWeight.BOLD, color=AZUL_ESCURO),
                atalho(ft.Icons.ADD_BOX_OUTLINED, "Cadastro de produtos",
                       "Área para cadastrar e gerenciar produtos.",
                       "produtos"),
                atalho(ft.Icons.CALENDAR_MONTH_OUTLINED,
                       "Controle de validade",
                       "Acompanhe os lotes e seus vencimentos.",
                       "validade"),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def tela_produtos():
        campos = {
            "nome": ft.TextField(label="Nome *", width=260),
            "categoria": ft.TextField(label="Categoria", width=200),
            "marca": ft.TextField(label="Marca", width=200),
            "codigo_barras": ft.TextField(label="Código de barras",
                                          width=200),
            "fornecedor": ft.TextField(label="Fornecedor", width=240),
            "preco_custo": ft.TextField(label="Preço de custo", width=160),
            "preco_venda": ft.TextField(label="Preço de venda *", width=160),
            "data_entrega": ft.TextField(label="Entrega (dd/mm/aaaa) *",
                                         width=200),
            "data_validade": ft.TextField(label="Validade (dd/mm/aaaa) *",
                                          width=200),
            "quantidade": ft.TextField(label="Quantidade *", width=140),
            "quantidade_minima": ft.TextField(label="Qtd. mínima", width=140),
            "lote": ft.TextField(label="Lote", width=160),
            "localizacao": ft.TextField(label="Localização", width=200),
        }

        mensagem = ft.Text("", size=13)
        vazio = ft.Text(
            "Nenhum produto cadastrado ainda. Preencha o formulário e "
            "clique em Salvar produto.",
            color=TEXTO_SUAVE, size=13, visible=False,
        )
        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t, weight=ft.FontWeight.BOLD,
                                      color=AZUL_ESCURO))
                for t in ["ID", "Produto", "Categoria", "Validade",
                          "Quantidade", "Local", "Ações"]
            ],
            rows=[],
            column_spacing=28,
        )

        def avisar(texto, erro=False):
            mensagem.value = texto
            mensagem.color = VERMELHO if erro else VERDE

        def carregar_tabela():
            try:
                produtos = listar_produtos()
            except Exception as erro:
                tabela.rows = []
                avisar(f"Não foi possível ler os produtos do banco: {erro}",
                       erro=True)
                return
            tabela.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(id_p))),
                        ft.DataCell(ft.Text(nome)),
                        ft.DataCell(ft.Text(categoria or "-")),
                        ft.DataCell(ft.Text(formatar_data(validade))),
                        ft.DataCell(ft.Text(str(qtd))),
                        ft.DataCell(ft.Text(local or "-")),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=VERMELHO,
                                tooltip="Excluir produto",
                                on_click=lambda e, i=id_p, n=nome:
                                    pedir_exclusao(i, n),
                            )
                        ),
                    ]
                )
                for id_p, nome, categoria, validade, qtd, local in produtos
            ]
            vazio.visible = not produtos

        def salvar(e):
            valores = {chave: (campo.value or "").strip()
                       for chave, campo in campos.items()}
            try:
                preco_venda = float(valores["preco_venda"].replace(",", "."))
                preco_custo = (float(valores["preco_custo"].replace(",", "."))
                               if valores["preco_custo"] else 0)
                entrega = converter_data(valores["data_entrega"])
                validade = converter_data(valores["data_validade"])
                quantidade = int(valores["quantidade"])
                minima = (int(valores["quantidade_minima"])
                          if valores["quantidade_minima"] else 5)
            except ValueError:
                avisar("Confira os campos com *: preço de venda (ex.: 25,90), "
                       "datas no formato dd/mm/aaaa e quantidade em números "
                       "inteiros.", erro=True)
                page.update()
                return

            if not valores["nome"]:
                avisar("Informe o nome do produto.", erro=True)
                page.update()
                return
            if validade < entrega:
                avisar("A validade não pode ser anterior à data de entrega.",
                       erro=True)
                page.update()
                return

            try:
                inserir_produto(
                    valores["nome"], valores["categoria"], valores["marca"],
                    valores["codigo_barras"] or None,  # vazio vira NULL
                    valores["fornecedor"], preco_custo, preco_venda,
                    entrega, validade, quantidade, minima,
                    valores["lote"], valores["localizacao"],
                )
            except Exception as erro:
                avisar(f"Não foi possível salvar o produto: {erro}",
                       erro=True)
                page.update()
                return

            for campo in campos.values():
                campo.value = ""
            avisar(f"Produto '{valores['nome']}' salvo com sucesso.")
            carregar_tabela()
            page.update()

        def limpar_campos(e):
            for campo in campos.values():
                campo.value = ""
            avisar("")
            page.update()

        def pedir_exclusao(id_produto, nome):
            def confirmar(e):
                fechar_dialogo(page, dialogo)
                try:
                    deletar_produto(id_produto)
                except Exception as erro:
                    avisar(f"Não foi possível excluir o produto: {erro}",
                           erro=True)
                    page.update()
                    return
                avisar(f"Produto '{nome}' excluído.")
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

        carregar_tabela()

        return ft.Column(
            controls=[
                cabecalho("Produtos",
                          "Cadastre, consulte e exclua os produtos do mercado."),
                ft.Divider(color="#DCE3EA"),
                ft.Container(
                    bgcolor=BRANCO, padding=18, border_radius=12,
                    content=ft.Column(
                        controls=[
                            ft.Text("Novo produto", size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=AZUL_ESCURO),
                            ft.Row(controls=list(campos.values()),
                                   wrap=True, spacing=12, run_spacing=12),
                            ft.Row(
                                controls=[
                                    ft.Button(
                                        "Salvar produto",
                                        icon=ft.Icons.SAVE_OUTLINED,
                                        on_click=salvar,
                                        style=ft.ButtonStyle(bgcolor=AZUL,
                                                             color=BRANCO),
                                    ),
                                    ft.OutlinedButton("Limpar campos",
                                                      on_click=limpar_campos),
                                ],
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

    def tela_lista(titulo, subtitulo, titulos, buscar, texto_vazio):
        erro_banco = ""
        linhas = []
        try:
            linhas = buscar()
        except Exception as erro:
            erro_banco = f"Não foi possível ler o banco de dados: {erro}"

        controles = [
            cabecalho(titulo, subtitulo),
            ft.Divider(color="#DCE3EA"),
        ]
        if erro_banco:
            controles.append(ft.Text(erro_banco, color=VERMELHO, size=13))
        elif not linhas:
            controles.append(ft.Text(texto_vazio, color=TEXTO_SUAVE, size=13))
        else:
            controles.append(painel(montar_tabela(titulos, linhas)))

        return ft.Column(controls=controles, spacing=16,
                         scroll=ft.ScrollMode.AUTO, expand=True)

    def tela_lotes():
        return tela_lista(
            "Lotes", "Lotes registrados, com validade e quantidade.",
            ["Lote", "Produto", "Validade", "Quantidade", "Local"],
            linhas_lotes,
            "Nenhum lote registrado ainda. Cadastre um produto na tela "
            "Produtos.",
        )

    def tela_estoque():
        return tela_lista(
            "Estoque", "Quantidade atual de cada produto e o mínimo desejado.",
            ["Produto", "Quantidade", "Mínimo", "Situação", "Atualizado em"],
            linhas_estoque,
            "O estoque está vazio. Cadastre um produto na tela Produtos.",
        )

    def tela_validade():
        return tela_lista(
            "Controle de validade",
            "Produtos vencidos, que vencem em até 7 dias ou com estoque baixo.",
            ["ID", "Produto", "Validade", "Prazo", "Quantidade", "Mínimo",
             "Alerta"],
            linhas_validade,
            "Nenhum alerta no momento. Tudo dentro da validade e do estoque "
            "mínimo.",
        )

    telas = {
        "inicio": tela_inicio,
        "produtos": tela_produtos,
        "lotes": tela_lotes,
        "estoque": tela_estoque,
        "validade": tela_validade,
    }

    menu = ft.Container(
        width=235,
        bgcolor=AZUL_ESCURO,
        padding=18,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Image(
                        src="logo_sao_jose.png",
                        width=165,
                        height=165,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(
                    "MERCADINHO SÃO JOSÉ",
                    color=BRANCO,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color="#52749A"),
                ft.Text("MENU PRINCIPAL", color="#BBD8F5", size=11,
                        weight=ft.FontWeight.BOLD),
                item_menu("inicio", ft.Icons.DASHBOARD_OUTLINED, "Início"),
                item_menu("produtos", ft.Icons.INVENTORY_2_OUTLINED,
                          "Produtos"),
                item_menu("lotes", ft.Icons.LAYERS_OUTLINED, "Lotes"),
                item_menu("estoque", ft.Icons.WAREHOUSE_OUTLINED, "Estoque"),
                item_menu("validade", ft.Icons.CALENDAR_MONTH_OUTLINED,
                          "Validade"),
                ft.Container(expand=True),
                ft.Text("Sistema de Controle de Estoque",
                        color="#BBD8F5", size=10),
            ],
            spacing=10,
            expand=True,
        ),
    )

    page.add(
        ft.Row(
            controls=[menu, area],
            spacing=0,
            expand=True,
        )
    )
    mostrar("inicio")


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")