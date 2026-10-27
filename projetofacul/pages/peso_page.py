"""Tela /peso: resumo, formulário de registro, histórico e exclusão."""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.logic.peso import SEM_VALOR
from projetofacul.states.peso_state import PesoState
from styles.theme import apply_theme_tokens

ROTA = "/peso"

PESO_PAGE_CSS = apply_theme_tokens("""
.peso-page { width: min(1200px, 100%); margin: 0 auto; display: grid; gap: 20px; }
.peso-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.peso-header-icon {
  width: 40px; height: 40px; flex: none; display: grid; place-items: center; border-radius: 50%;
  color: __PRIMARY__; background: rgba(43,140,255,.14);
}
.peso-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.peso-subtitle { margin: 0; color: __TEXT_SECONDARY__; font-size: 15.5px; line-height: 1.6; }

.peso-card, .peso-summary-card, .peso-item {
  border: 1px solid __BORDER__; border-radius: 16px; background: __SURFACE__;
  transition: border-color 170ms ease, transform 170ms ease, box-shadow 170ms ease;
}
.peso-summary-card:hover, .peso-item:hover { border-color: rgba(59,147,255,.35); transform: translateY(-2px); box-shadow: 0 14px 34px rgba(0,0,0,.22); }

.peso-summary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.peso-summary-card { padding: 18px 20px; }
.peso-summary-label { margin: 0 0 8px; color: __TEXT_SECONDARY__; font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.peso-summary-value { margin: 0; font-size: 28px; line-height: 1.1; font-weight: 700; }
.peso-summary-caption { margin: 6px 0 0; color: __TEXT_MUTED__; font-size: 12.5px; }

.peso-card { padding: 22px 24px; }
.peso-card-title { margin: 0 0 16px; font-size: 17px; font-weight: 800; }
.peso-form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.peso-field { display: grid; gap: 7px; min-width: 0; align-content: start; }
.peso-label { color: #E8EEF8; font-size: 13px; font-weight: 650; }
.peso-input {
  width: 100%; min-height: 44px; padding: 0 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 10px;
  color: __TEXT_PRIMARY__; background: rgba(5,12,24,.54); font: inherit; font-size: 14.5px; color-scheme: dark;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
.peso-input:focus { outline: none; border-color: __PRIMARY__; box-shadow: 0 0 0 3px rgba(43,140,255,.18); }
.peso-input[aria-invalid="true"] { border-color: #D6818B; }
.peso-error-text { margin: 0; min-height: 0; color: #F0A1A9; font-size: 12.5px; line-height: 1.4; }
.peso-global-error { margin: 16px 0 0; padding: 10px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px; color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px; }
.peso-form-actions { display: flex; justify-content: flex-end; margin-top: 18px; }

.peso-button {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 20px;
  border: 0; border-radius: 10px; color: #FFFFFF; background: __PRIMARY__; font: inherit; font-size: 14.5px;
  font-weight: 700; white-space: nowrap; cursor: pointer; box-shadow: 0 10px 24px rgba(43,140,255,.18);
  transition: transform 170ms ease, box-shadow 170ms ease, background 170ms ease, opacity 170ms ease;
}
.peso-button:hover:not(:disabled) { transform: translateY(-1px); background: __PRIMARY_HOVER__; box-shadow: 0 14px 30px rgba(43,140,255,.26); }
.peso-button:active:not(:disabled) { transform: scale(.98); }
.peso-button:disabled { opacity: .72; cursor: wait; }
.peso-button-secondary {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 18px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.peso-button-secondary:hover { background: rgba(255,255,255,.06); }
.peso-button-secondary:active { transform: scale(.98); }
.peso-button-danger { background: #D9475A; box-shadow: none; }
.peso-button-danger:hover:not(:disabled) { background: #E35D6F; box-shadow: none; }
.peso-button:focus-visible, .peso-button-secondary:focus-visible, .peso-delete:focus-visible {
  outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px;
}

.peso-list-title { margin: 6px 0 14px; font-size: 18px; font-weight: 800; }
.peso-list { display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }
.peso-item { display: flex; align-items: center; gap: 16px; padding: 16px 20px; animation: peso-fade-in 260ms ease both; }
.peso-item-info { min-width: 0; flex: 1; }
.peso-item-weight { margin: 0; font-size: 20px; font-weight: 800; }
.peso-item-date { margin: 4px 0 0; color: __TEXT_SECONDARY__; font-size: 13.5px; }
.peso-delete {
  width: 44px; height: 44px; flex: none; display: grid; place-items: center; border: 0; border-radius: 10px;
  color: #F0707F; background: transparent; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.peso-delete:hover { background: rgba(240,112,127,.12); }
.peso-delete:active { transform: scale(.96); }

.peso-empty {
  display: grid; justify-items: center; gap: 10px; padding: 44px 24px; border: 1.5px dashed rgba(255,255,255,.16);
  border-radius: 18px; text-align: center;
}
.peso-empty-title { margin: 6px 0 0; font-size: 18px; font-weight: 800; }
.peso-empty-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; }
.peso-error { display: grid; justify-items: center; gap: 12px; padding: 32px 24px; border: 1px solid rgba(240,161,169,.24); border-radius: 16px; background: rgba(130,35,48,.12); text-align: center; }
.peso-error p { margin: 0; color: #F2B1B7; }
.peso-skeleton { height: 76px; border-radius: 16px; background: linear-gradient(90deg, rgba(255,255,255,.04), rgba(255,255,255,.09), rgba(255,255,255,.04)); background-size: 200% 100%; animation: peso-shimmer 1.2s ease-in-out infinite; }

.peso-alert { max-width: 420px !important; color: __TEXT_PRIMARY__; background: __SURFACE__ !important; border: 1px solid __BORDER__; border-radius: 16px !important; font-family: __FONT__; animation: peso-pop 180ms cubic-bezier(.2,.8,.2,1) both; }
.peso-alert-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
.rt-AlertDialogOverlay { background: rgba(3,8,18,.72) !important; }

@keyframes peso-fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes peso-pop { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }
@keyframes peso-shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }

@media (max-width: 640px) {
  .peso-title { font-size: 27px; }
  .peso-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .peso-summary-card:first-child { grid-column: 1 / -1; }
  .peso-summary-card { padding: 14px 16px; }
  .peso-summary-value { font-size: 23px; }
  .peso-card { padding: 18px 16px; }
  .peso-form-grid { grid-template-columns: minmax(0, 1fr); }
  .peso-form-actions .peso-button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  .peso-item, .peso-alert, .peso-skeleton { animation: none !important; }
  .peso-summary-card:hover, .peso-item:hover { transform: none; }
}
""")


def page_header() -> rx.Component:
    return rx.el.header(
        rx.box(
            rx.box(rx.icon(tag="scale", size=20, aria_hidden="true"), class_name="peso-header-icon"),
            rx.el.h1("Peso corporal", class_name="peso-title"),
            class_name="peso-header-row",
        ),
        rx.el.p("Registre seu peso e acompanhe as variações.", class_name="peso-subtitle"),
    )


def summary_card(rotulo: str, valor, legenda: str = "") -> rx.Component:
    return rx.box(
        rx.el.p(rotulo, class_name="peso-summary-label"),
        rx.el.p(valor, class_name="peso-summary-value"),
        rx.el.p(legenda, class_name="peso-summary-caption") if legenda else rx.fragment(),
        class_name="peso-summary-card",
    )


def summary_cards() -> rx.Component:
    return rx.el.section(
        summary_card("Peso atual", PesoState.peso_atual),
        summary_card("Desde o 1º registro", PesoState.variacao),
        # TODO: integração futura com IA (falta para a meta) — exige um peso-alvo
        # (ex.: `peso_meta`) que ainda não existe no Xano; até lá, nada é calculado.
        summary_card("Falta para a meta", SEM_VALOR, "Disponível em breve"),
        aria_label="Resumo do peso",
        class_name="peso-summary",
    )


def field_error(campo: str, input_id: str) -> rx.Component:
    return rx.el.p(
        PesoState.erros.get(campo, ""),
        id=f"{input_id}-erro",
        aria_live="polite",
        class_name="peso-error-text",
    )


def form_field(rotulo: str, campo: str, input_id: str, **props) -> rx.Component:
    return rx.box(
        rx.el.label(rotulo, html_for=input_id, class_name="peso-label"),
        rx.el.input(
            id=input_id,
            name=campo,
            value=getattr(PesoState, campo),
            on_change=lambda valor: PesoState.update_field(campo, valor),
            aria_invalid=PesoState.erros.contains(campo),
            aria_describedby=f"{input_id}-erro",
            class_name="peso-input",
            **props,
        ),
        field_error(campo, input_id),
        class_name="peso-field",
    )


def weight_form() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Novo registro", id="peso-form-titulo", class_name="peso-card-title"),
        rx.form(
            rx.box(
                form_field("Data", "data", "peso-data", type="date", max=PesoState.hoje),
                form_field("Horário", "horario", "peso-horario", type="time"),
                form_field(
                    "Peso (kg)",
                    "peso",
                    "peso-valor",
                    type="text",
                    input_mode="decimal",
                    auto_complete="off",
                    placeholder="Ex.: 70,5",
                ),
                class_name="peso-form-grid",
            ),
            rx.cond(
                PesoState.erro_geral != "",
                rx.el.p(PesoState.erro_geral, role="status", aria_live="polite", class_name="peso-global-error"),
                rx.fragment(),
            ),
            rx.box(
                rx.el.button(
                    rx.cond(PesoState.salvando, rx.spinner(size="2"), rx.icon(tag="save", size=17, aria_hidden="true")),
                    "Salvar registro",
                    type="submit",
                    title="Registra o peso no seu histórico",
                    disabled=PesoState.salvando,
                    aria_busy=PesoState.salvando,
                    class_name="peso-button",
                ),
                class_name="peso-form-actions",
            ),
            on_submit=PesoState.save_weight,
        ),
        aria_labelledby="peso-form-titulo",
        class_name="peso-card",
    )


def weight_item(registro) -> rx.Component:
    return rx.el.li(
        rx.box(
            rx.el.p(registro["peso"], class_name="peso-item-weight"),
            rx.el.p(registro["data_hora"], class_name="peso-item-date"),
            class_name="peso-item-info",
        ),
        rx.el.button(
            rx.icon(tag="trash-2", size=18, aria_hidden="true"),
            type="button",
            aria_label=f"Excluir registro de {registro['peso']} em {registro['data_hora']}",
            title="Excluir este registro",
            on_click=PesoState.ask_delete(registro["id"]),
            class_name="peso-delete",
        ),
        class_name="peso-item",
    )


def empty_state() -> rx.Component:
    return rx.box(
        rx.box(rx.icon(tag="scale", size=22, aria_hidden="true"), class_name="peso-header-icon"),
        rx.el.p("Nenhum peso registrado ainda", class_name="peso-empty-title"),
        rx.el.p("Registre seu peso de hoje para começar a acompanhar sua evolução.", class_name="peso-empty-text"),
        class_name="peso-empty",
    )


def list_error() -> rx.Component:
    return rx.box(
        rx.el.p(PesoState.erro_lista, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            title="Busca seus registros de peso de novo",
            on_click=PesoState.start_page,
            class_name="peso-button-secondary",
        ),
        class_name="peso-error",
    )


def weight_list() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Histórico", id="peso-historico-titulo", class_name="peso-list-title"),
        rx.el.ul(rx.foreach(PesoState.registros, weight_item), class_name="peso-list"),
        aria_labelledby="peso-historico-titulo",
    )


def loading_list() -> rx.Component:
    return rx.box(
        rx.box(class_name="peso-skeleton"),
        rx.box(class_name="peso-skeleton"),
        class_name="peso-list",
        aria_busy="true",
        aria_label="Carregando registros de peso",
    )


def delete_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Excluir este registro?"),
            rx.alert_dialog.description("O peso sai do seu histórico e do resumo. Essa ação não pode ser desfeita."),
            rx.box(
                rx.alert_dialog.cancel(
                    rx.el.button("Cancelar", type="button", title="Mantém o registro", class_name="peso-button-secondary"),
                ),
                rx.el.button(
                    rx.cond(PesoState.excluindo, rx.spinner(size="2"), rx.icon(tag="trash-2", size=16, aria_hidden="true")),
                    "Excluir",
                    type="button",
                    title="Exclui o registro definitivamente",
                    on_click=PesoState.confirm_delete,
                    disabled=PesoState.excluindo,
                    class_name="peso-button peso-button-danger",
                ),
                class_name="peso-alert-actions",
            ),
            class_name="peso-alert",
        ),
        open=PesoState.exclusao_id != "",
        on_open_change=PesoState.set_delete_open,
    )


def peso_page() -> rx.Component:
    tem_registros = PesoState.registros.length() > 0
    # vazio: formulário + estado vazio; com registros: resumo + formulário + lista
    return app_shell(
        ROTA,
        rx.box(
            page_header(),
            rx.cond(PesoState.carregando, rx.fragment(), rx.cond(tem_registros, summary_cards(), rx.fragment())),
            weight_form(),
            rx.cond(
                PesoState.carregando,
                loading_list(),
                rx.cond(
                    PesoState.erro_lista != "",
                    list_error(),
                    rx.cond(tem_registros, weight_list(), empty_state()),
                ),
            ),
            delete_dialog(),
            class_name="peso-page",
        ),
        PESO_PAGE_CSS,
    )
