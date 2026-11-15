"""Interface dos alertas: sino com contador, painel e aviso ao abrir o sistema."""
import flet as ft

from componentes.ui import abrir_dialogo, etiqueta, fechar_dialogo
from funcoes.alertas import (BAIXO, DIAS_URGENTE, PROXIMO, VENCIDO,
                             carregar_alertas)
from tema import (AMARELO, AZUL, AZUL_ESCURO, BRANCO, LARANJA, TEXTO_SUAVE,
                  VERMELHO)
from utils.erros import registrar_erro


def cor_do_alerta(alerta):
    if alerta.urgente:
        return VERMELHO
    if alerta.tipo == PROXIMO:
        return AMARELO
    if alerta.tipo == BAIXO:
        return LARANJA
    return AZUL


def linha_alerta(alerta):
    """Uma linha: etiqueta colorida + descrição."""
    chip = etiqueta(alerta.rotulo, cor_do_alerta(alerta))
    chip.width = 140
    chip.alignment = ft.Alignment(0, 0)
    return ft.Row(
        controls=[chip,
                  ft.Text(alerta.descricao, size=13, color=AZUL_ESCURO,
                          expand=True)],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def abrir_painel(page, navegar):
    """Diálogo com todos os alertas atuais (consulta o banco na hora)."""
    resultado = carregar_alertas(forcar=True)

    if resultado.erro:
        corpo = ft.Text(resultado.erro, color=VERMELHO, size=13)
    elif not resultado.alertas:
        corpo = ft.Text("Nenhum alerta no momento. Tudo dentro da validade e "
                        "do estoque mínimo.", color=TEXTO_SUAVE, size=13)
    else:
        altura = min(46 * len(resultado.alertas) + 10, 360)
        corpo = ft.Container(
            width=620, height=altura,
            content=ft.Column(
                controls=[linha_alerta(a) for a in resultado.alertas],
                spacing=10, scroll=ft.ScrollMode.AUTO,
            ),
        )

    def fechar(e):
        fechar_dialogo(page, dialogo)

    def abrir_validade(e):
        fechar_dialogo(page, dialogo)
        navegar("validade")

    total = len(resultado.alertas)
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Alertas ({total})" if total else "Alertas"),
        content=corpo,
        actions=[
            ft.TextButton("Fechar", on_click=fechar),
            ft.Button("Abrir controle de validade", on_click=abrir_validade,
                      style=ft.ButtonStyle(bgcolor=AZUL, color=BRANCO)),
        ],
    )
    abrir_dialogo(page, dialogo)


class Sino:
    """Sino do cabeçalho com um selo mostrando quantos alertas existem.

    Vermelho = há algo vencido ou urgente; amarelo = só avisos menores.
    Use `atualizar()` depois de mudar produtos para o número acompanhar.
    """

    def __init__(self, page, navegar):
        self.page = page
        self.navegar = navegar
        self._numero = ft.Text("", size=10, color=BRANCO,
                               weight=ft.FontWeight.BOLD)
        self._selo = ft.Container(
            content=self._numero, width=18, height=18, border_radius=9,
            bgcolor=VERMELHO, alignment=ft.Alignment(0, 0), visible=False,
            right=2, top=2,
        )
        self._botao = ft.IconButton(
            icon=ft.Icons.NOTIFICATIONS_NONE, icon_color=AZUL,
            tooltip="Ver alertas", on_click=self._clicar,
        )
        self.controle = ft.Stack(width=48, height=48,
                                 controls=[self._botao, self._selo])
        self.atualizar()

    def atualizar(self):
        resultado = carregar_alertas()
        total = len(resultado.alertas)
        self._selo.visible = total > 0
        self._numero.value = "9+" if total > 9 else str(total)
        self._selo.bgcolor = VERMELHO if resultado.urgentes else AMARELO
        self._botao.tooltip = (f"{total} alerta(s)" if total
                               else "Nenhum alerta")

    def _clicar(self, e):
        try:
            abrir_painel(self.page, self.navegar)
        except Exception as erro:
            registrar_erro(erro, "abrir painel de alertas")


def avisar_alertas_urgentes(page, navegar):
    """Aviso ao abrir o sistema se houver vencidos ou produtos vencendo logo."""
    try:
        resultado = carregar_alertas()
        vencidos = len(resultado.por_tipo(VENCIDO))
        urgentes = len([a for a in resultado.urgentes if a.tipo == PROXIMO])
        if not (vencidos or urgentes):
            return
        partes = []
        if vencidos:
            partes.append(f"{vencidos} produto(s) vencido(s)")
        if urgentes:
            partes.append(f"{urgentes} vencendo em até {DIAS_URGENTE} dias")
        aviso = ft.SnackBar(
            content=ft.Text("Atenção: " + " e ".join(partes) + ".",
                            color=BRANCO),
            bgcolor=VERMELHO,
            action="Ver alertas",
            on_action=lambda e: navegar("validade"),
            duration=8000,
        )
        abrir_dialogo(page, aviso)
    except Exception as erro:
        registrar_erro(erro, "aviso de alertas ao iniciar")
