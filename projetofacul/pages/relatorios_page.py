"""Tela /relatorios: frequência de treinos, horas de sono, evolução do peso e calorias."""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.states.relatorios_state import RelatoriosState
from styles.theme import THEME, apply_theme_tokens

ROTA = "/relatorios"
MENSAGEM_SEM_DADOS = "Ainda não há dados suficientes."

# (relatório, título do card, cabeçalho da coluna de período na tabela acessível)
CARDS_RELATORIO = (
    ("treinos", "Frequência de treinos (últimas 8 semanas)", "Semana iniciada em"),
    ("sono", "Horas de sono (últimos 30 registros)", "Noite (acordou em)"),
    ("peso", "Evolução do peso", "Data"),
    ("calorias", "Calorias ingeridas x gastas (últimos 14 dias)", "Dia"),
)

TIPOS_GRAFICO_UI = (("colunas", "Colunas", "chart-column"), ("linhas", "Linhas", "chart-line"))

NOTAS_CALORIAS = (
    "Calorias estimadas por IA a partir das suas refeições; não substituem orientação de um nutricionista.",
    "As calorias gastas aparecerão quando a IA estimar seus treinos.",
)

# série única na cor da marca (validada: contraste >= 3:1 sobre a superfície escura)
COR_SERIE = THEME.COLORS["primary"]
COR_EIXO = THEME.COLORS["text_muted"]

# Recharts formata no navegador: o tooltip mostra o texto já pronto ("7,5 h")
# e o eixo Y usa o separador decimal brasileiro
FORMATO_TOOLTIP = rx.Var("(valor, nome, item) => [item.payload.texto, '']")
FORMATO_EIXO_Y = rx.Var("(valor) => Number(valor).toLocaleString('pt-BR')")

RELATORIOS_PAGE_CSS = apply_theme_tokens("""
.rel-page { width: min(960px, 100%); display: grid; gap: 32px; }
.rel-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.rel-header-icon {
  width: 40px; height: 40px; flex: none; display: grid; place-items: center; border-radius: 50%;
  color: __PRIMARY__; background: rgba(43,140,255,.14);
}
.rel-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.rel-subtitle { margin: 0; color: __TEXT_SECONDARY__; font-size: 15.5px; line-height: 1.6; }
.rel-card {
  min-width: 0; padding: 22px 24px 24px; border: 1px solid rgba(255,255,255,.1); border-radius: 20px;
  background: linear-gradient(180deg, #16223A 0%, __SURFACE__ 100%); box-shadow: 0 18px 45px rgba(0,0,0,.25);
  animation: rel-rise 480ms cubic-bezier(.2,.8,.2,1) both;
}
.rel-card:nth-child(3) { animation-delay: 60ms; }
.rel-card:nth-child(4) { animation-delay: 120ms; }
.rel-card:nth-child(5) { animation-delay: 180ms; }
.rel-card-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.rel-card-title { margin: 0; font-size: 17px; line-height: 1.35; font-weight: 800; }
.rel-toggles {
  flex: none; display: inline-flex; gap: 4px; padding: 4px; border-radius: 999px; background: rgba(4,11,23,.55);
}
.rel-toggle {
  min-height: 32px; display: inline-flex; align-items: center; gap: 6px; padding: 0 12px;
  border: 0; border-radius: 999px; color: __TEXT_SECONDARY__; background: transparent;
  font: inherit; font-size: 13px; font-weight: 650; cursor: pointer; transition: color 150ms ease, background 150ms ease;
}
.rel-toggle:hover { color: __TEXT_PRIMARY__; }
.rel-toggle.is-active { color: __TEXT_PRIMARY__; background: #1A2940; box-shadow: 0 2px 8px rgba(0,0,0,.22); }
.rel-toggle:focus-visible, .rel-retry:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
.rel-body { min-height: 240px; display: grid; }
.rel-chart { min-width: 0; height: 240px; }
.rel-status { display: grid; place-items: center; align-content: center; gap: 12px; color: __TEXT_SECONDARY__; font-size: 14px; text-align: center; }
.rel-status p { margin: 0; }
.rel-error p { color: #F2B1B7; }
.rel-retry {
  min-height: 40px; display: inline-flex; align-items: center; gap: 8px; padding: 0 16px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 13.5px; font-weight: 650; cursor: pointer;
}
.rel-retry:hover { background: rgba(255,255,255,.06); }
.rel-notes { display: grid; gap: 6px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,.06); }
.rel-note { display: flex; align-items: flex-start; gap: 8px; margin: 0; color: __TEXT_SECONDARY__; font-size: 12.5px; line-height: 1.5; }
.rel-note svg { flex: none; margin-top: 2px; color: __PRIMARY__; }
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
}
@keyframes rel-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@media (pointer: coarse) {
  .rel-toggle, .rel-retry { min-height: 44px; }
}
@media (max-width: 520px) {
  .rel-card { padding: 18px 16px 20px; border-radius: 16px; }
  .rel-card-head { flex-direction: column; align-items: flex-start; }
  .rel-title { font-size: 28px; }
}
@media (prefers-reduced-motion: reduce) {
  .rel-card { animation: none; }
}
""")


def page_header() -> rx.Component:
    return rx.box(
        rx.box(
            rx.box(rx.icon(tag="chart-no-axes-combined", size=20, aria_hidden="true"), class_name="rel-header-icon"),
            rx.el.h1("Relatórios", class_name="rel-title"),
            class_name="rel-header-row",
        ),
        rx.el.p(
            "Acompanhe sua evolução com base nos seus registros de treino, sono, peso e refeições.",
            class_name="rel-subtitle",
        ),
    )


def chart_type_selector(relatorio: str, titulo: str, tipo) -> rx.Component:
    return rx.box(
        *[
            rx.el.button(
                rx.icon(tag=icone, size=15, aria_hidden="true"),
                rotulo,
                type="button",
                aria_pressed=tipo == valor,
                on_click=RelatoriosState.set_chart_type(relatorio, valor),
                class_name=rx.cond(tipo == valor, "rel-toggle is-active", "rel-toggle"),
            )
            for valor, rotulo, icone in TIPOS_GRAFICO_UI
        ],
        role="group",
        aria_label=f"Tipo de gráfico: {titulo}",
        class_name="rel-toggles",
    )


def chart_axes(relatorio: str, em_linhas: bool) -> list[rx.Component]:
    # colunas sempre a partir de 0; em linhas, o peso acompanha a faixa dos dados
    dominio = ["dataMin - 1", "dataMax + 1"] if em_linhas and relatorio == "peso" else [0, "auto"]
    estilo_tick = {"fill": COR_EIXO, "fontSize": 12}
    return [
        rx.recharts.cartesian_grid(vertical=False, stroke="rgba(255,255,255,.06)"),
        rx.recharts.x_axis(
            data_key="rotulo",
            tick=estilo_tick,
            tick_line=False,
            axis_line=False,
            interval="preserveStartEnd",
        ),
        rx.recharts.y_axis(
            tick=estilo_tick,
            tick_line=False,
            axis_line=False,
            width=44,
            domain=dominio,
            allow_decimals=relatorio in ("sono", "peso"),
            custom_attrs={"tickFormatter": FORMATO_EIXO_Y},
        ),
        rx.recharts.graphing_tooltip(
            separator="",
            cursor={"fill": "rgba(43,140,255,.08)", "stroke": "rgba(43,140,255,.35)"},
            content_style={
                "background": THEME.COLORS["surface"],
                "border": "1px solid rgba(255,255,255,.12)",
                "borderRadius": "10px",
            },
            label_style={"color": THEME.COLORS["text_secondary"]},
            item_style={"color": THEME.COLORS["text_primary"]},
            custom_attrs={"formatter": FORMATO_TOOLTIP},
        ),
    ]


def report_chart(relatorio: str, pontos, tipo) -> rx.Component:
    margem = {"top": 8, "right": 8, "left": 0, "bottom": 0}
    grafico_colunas = rx.recharts.bar_chart(
        *chart_axes(relatorio, em_linhas=False),
        rx.recharts.bar(
            data_key="valor",
            fill=COR_SERIE,
            radius=[4, 4, 0, 0],
            max_bar_size=28,
            is_animation_active=False,
        ),
        data=pontos,
        margin=margem,
        height=240,
    )
    grafico_linhas = rx.recharts.line_chart(
        *chart_axes(relatorio, em_linhas=True),
        rx.recharts.line(
            data_key="valor",
            type_="monotone",
            stroke=COR_SERIE,
            stroke_width=2,
            dot={"r": 4, "fill": COR_SERIE, "stroke": THEME.COLORS["surface"], "strokeWidth": 2},
            active_dot={"r": 6, "fill": COR_SERIE, "stroke": THEME.COLORS["surface"], "strokeWidth": 2},
            # dia sem valor é lacuna, nunca zero
            connect_nulls=False,
            is_animation_active=False,
        ),
        data=pontos,
        margin=margem,
        height=240,
    )
    return rx.box(rx.cond(tipo == "linhas", grafico_linhas, grafico_colunas), class_name="rel-chart")


def data_table(relatorio: str, titulo: str, rotulo_periodo: str, pontos) -> rx.Component:
    return rx.el.table(
        rx.el.caption(titulo),
        rx.el.thead(rx.el.tr(rx.el.th(rotulo_periodo, scope="col"), rx.el.th("Valor", scope="col"))),
        rx.el.tbody(
            rx.foreach(pontos, lambda ponto: rx.el.tr(rx.el.td(ponto["rotulo"]), rx.el.td(ponto["texto"]))),
        ),
        id=f"rel-{relatorio}-tabela",
        class_name="sr-only",
    )


def card_error(erro) -> rx.Component:
    return rx.box(
        rx.el.p(erro, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            on_click=RelatoriosState.start_page,
            class_name="rel-retry",
        ),
        class_name="rel-status rel-error",
    )


def card_notes(notas: tuple[str, ...]) -> rx.Component:
    return rx.box(
        *[rx.el.p(rx.icon(tag="info", size=14, aria_hidden="true"), nota, class_name="rel-note") for nota in notas],
        class_name="rel-notes",
    )


def report_card(relatorio: str, titulo: str, rotulo_periodo: str) -> rx.Component:
    pontos = getattr(RelatoriosState, f"pontos_{relatorio}")
    tipo = getattr(RelatoriosState, f"tipo_{relatorio}")
    erro = getattr(RelatoriosState, f"erro_{relatorio}")
    suficiente = getattr(RelatoriosState, f"suficiente_{relatorio}")
    titulo_id = f"rel-{relatorio}-titulo"

    corpo = rx.cond(
        RelatoriosState.carregando,
        rx.box(rx.spinner(size="3", aria_label="Carregando"), class_name="rel-status"),
        rx.cond(
            erro != "",
            card_error(erro),
            rx.cond(
                suficiente,
                rx.fragment(
                    report_chart(relatorio, pontos, tipo),
                    data_table(relatorio, titulo, rotulo_periodo, pontos),
                ),
                rx.box(rx.el.p(MENSAGEM_SEM_DADOS), class_name="rel-status"),
            ),
        ),
    )

    return rx.el.section(
        rx.box(
            rx.el.h2(titulo, id=titulo_id, class_name="rel-card-title"),
            chart_type_selector(relatorio, titulo, tipo),
            class_name="rel-card-head",
        ),
        rx.box(corpo, class_name="rel-body", aria_describedby=f"rel-{relatorio}-tabela"),
        card_notes(NOTAS_CALORIAS) if relatorio == "calorias" else rx.fragment(),
        aria_labelledby=titulo_id,
        class_name="rel-card",
    )


def relatorios_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(
            page_header(),
            *[report_card(relatorio, titulo, periodo) for relatorio, titulo, periodo in CARDS_RELATORIO],
            class_name="rel-page",
        ),
        RELATORIOS_PAGE_CSS,
    )
