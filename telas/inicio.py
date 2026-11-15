"""Tela inicial: resumo do estoque e atalhos."""
import flet as ft

from componentes.alertas_ui import Sino, linha_alerta
from componentes.ui import cabecalho, criar_cartao
from funcoes.alertas import carregar_alertas
from funcoes.estoque import resumo_estoque
from tema import (AMARELO, AZUL, AZUL_ESCURO, BRANCO, LINHA, TEXTO_SUAVE,
                  VERMELHO)
from utils.erros import mensagem_amigavel, registrar_erro


def _atalho(icone, titulo, descricao, destino, navegar):
    return ft.Container(
        bgcolor=BRANCO, padding=18, border_radius=12, ink=True,
        on_click=lambda e: navegar(destino),
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


def _destaque_alertas(resultado, navegar):
    """Caixa com os 5 alertas mais graves (ou vazio se não houver nenhum)."""
    if not resultado.alertas:
        return ft.Container(visible=False)
    primeiros = resultado.alertas[:5]
    restante = len(resultado.alertas) - len(primeiros)
    texto_botao = ("Ver todos os alertas" if restante <= 0
                   else f"Ver todos os alertas (+{restante})")
    return ft.Container(
        bgcolor=BRANCO, padding=18, border_radius=12,
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
                            color=VERMELHO if resultado.urgentes else AMARELO),
                    ft.Text("Alertas em destaque", size=16,
                            weight=ft.FontWeight.BOLD, color=AZUL_ESCURO),
                ]),
                *[linha_alerta(a) for a in primeiros],
                ft.TextButton(texto_botao,
                              on_click=lambda e: navegar("validade")),
            ],
            spacing=10,
        ),
    )


def criar_tela(page, navegar):
    sino = Sino(page, navegar)
    resultado = carregar_alertas(forcar=True)
    sino.atualizar()
    aviso = ""
    try:
        produtos, lotes, proximos, vencidos = resumo_estoque()
    except Exception as erro:
        registrar_erro(erro, "carregar tela inicial")
        produtos = lotes = proximos = vencidos = 0
        aviso = mensagem_amigavel(erro)

    return ft.Column(
        controls=[
            cabecalho("Visão geral",
                      "Bem-vindo ao sistema do Mercadinho São José!", sino),
            ft.Divider(color=LINHA),
            ft.Text(aviso, color=VERMELHO, size=13, visible=bool(aviso)),
            _destaque_alertas(resultado, navegar),
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
                                 ft.Icons.WARNING_AMBER_OUTLINED, VERMELHO),
                ],
                spacing=14,
            ),
            ft.Text("Acesso rápido", size=18,
                    weight=ft.FontWeight.BOLD, color=AZUL_ESCURO),
            _atalho(ft.Icons.ADD_BOX_OUTLINED, "Cadastro de produtos",
                    "Área para cadastrar e gerenciar produtos.",
                    "produtos", navegar),
            _atalho(ft.Icons.CALENDAR_MONTH_OUTLINED, "Controle de validade",
                    "Acompanhe os lotes e seus vencimentos.",
                    "validade", navegar),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
