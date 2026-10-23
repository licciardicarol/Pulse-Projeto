"""Tela /refeicoes: totais do dia, histórico, modal "Nova refeição" e exclusão."""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.logic.refeicoes import OPCOES_TIPO, TAMANHO_MAXIMO_DESCRICAO
from projetofacul.states.refeicoes_state import RefeicoesState
from styles.theme import apply_theme_tokens

ROTA = "/refeicoes"

REFEICOES_PAGE_CSS = apply_theme_tokens("""
.ref-page { width: min(1200px, 100%); margin: 0 auto; }
.ref-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 24px; }
.ref-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.ref-header-icon {
  width: 40px; height: 40px; flex: none; display: grid; place-items: center; border-radius: 50%;
  color: __PRIMARY__; background: rgba(43,140,255,.14);
}
.ref-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.ref-subtitle { margin: 0; max-width: 640px; color: __TEXT_SECONDARY__; font-size: 15.5px; line-height: 1.6; }
.ref-button {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 20px;
  border: 0; border-radius: 10px; color: #FFFFFF; background: __PRIMARY__; font: inherit; font-size: 14.5px;
  font-weight: 700; white-space: nowrap; cursor: pointer; box-shadow: 0 10px 24px rgba(43,140,255,.18);
  transition: transform 170ms ease, box-shadow 170ms ease, background 170ms ease, opacity 170ms ease;
}
.ref-button:hover:not(:disabled) { transform: translateY(-1px); background: __PRIMARY_HOVER__; box-shadow: 0 14px 30px rgba(43,140,255,.26); }
.ref-button:active:not(:disabled) { transform: scale(.98); }
.ref-button:disabled { opacity: .72; cursor: wait; }
.ref-button-secondary {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 18px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.ref-button-secondary:hover { background: rgba(255,255,255,.06); }
.ref-button-secondary:active { transform: scale(.98); }
.ref-button-danger { background: #D9475A; box-shadow: none; }
.ref-button-danger:hover:not(:disabled) { background: #E35D6F; box-shadow: none; }
.ref-button:focus-visible, .ref-button-secondary:focus-visible, .ref-delete:focus-visible, .ref-close:focus-visible,
.ref-input:focus-visible, .ref-select:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }

.ref-totals { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.ref-total, .ref-item {
  border: 1px solid __BORDER__; border-radius: 16px; background: __SURFACE__;
  transition: border-color 170ms ease, transform 170ms ease, box-shadow 170ms ease;
}
.ref-total { padding: 18px 20px; }
.ref-total:hover, .ref-item:hover { border-color: rgba(59,147,255,.35); transform: translateY(-2px); box-shadow: 0 14px 34px rgba(0,0,0,.22); }
.ref-total-label { margin: 0 0 8px; color: __TEXT_SECONDARY__; font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.ref-total-value { margin: 0; font-size: 28px; line-height: 1.1; font-weight: 700; }
.ref-total-unit { margin-left: 4px; color: __TEXT_SECONDARY__; font-size: 14px; font-weight: 600; }
.ref-pending-note { margin: 12px 0 0; color: __TEXT_MUTED__; font-size: 13px; }

.ref-list-section { margin-top: 30px; }
.ref-list-title { margin: 0 0 14px; font-size: 18px; font-weight: 800; }
.ref-list { display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }
.ref-item { padding: 18px 20px; animation: ref-fade-in 260ms ease both; }
.ref-item-top { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; }
.ref-chip {
  display: inline-flex; align-items: center; min-height: 26px; padding: 0 10px; border-radius: 999px;
  color: #8EBEFF; background: rgba(43,140,255,.14); font-size: 12.5px; font-weight: 700;
}
.ref-date { color: __TEXT_SECONDARY__; font-size: 13px; }
.ref-calories { margin-left: auto; color: __PRIMARY__; font-size: 15px; font-weight: 700; }
.ref-item-top .ref-delete { margin-left: auto; }
.ref-calories + .ref-delete { margin-left: 0; }
.ref-delete {
  width: 44px; height: 44px; display: grid; place-items: center; border: 0; border-radius: 10px;
  color: #F0707F; background: transparent; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.ref-delete:hover { background: rgba(240,112,127,.12); }
.ref-delete:active { transform: scale(.96); }
.ref-description { margin: 0; font-size: 15.5px; font-weight: 600; line-height: 1.5; overflow-wrap: anywhere; white-space: pre-line; }
.ref-macros { margin: 8px 0 0; color: __TEXT_SECONDARY__; font-size: 13.5px; }
.ref-pending-badge {
  display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; min-height: 24px; padding: 0 10px;
  border-radius: 999px; color: __TEXT_SECONDARY__; background: rgba(255,255,255,.05); font-size: 12px; font-weight: 600;
}

.ref-empty {
  display: grid; justify-items: center; gap: 10px; padding: 44px 24px; border: 1.5px dashed rgba(255,255,255,.16);
  border-radius: 18px; text-align: center;
}
.ref-empty-title { margin: 6px 0 0; font-size: 18px; font-weight: 800; }
.ref-empty-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; }
.ref-error { display: grid; justify-items: center; gap: 12px; padding: 32px 24px; border: 1px solid rgba(240,161,169,.24); border-radius: 16px; background: rgba(130,35,48,.12); text-align: center; }
.ref-error p { margin: 0; color: #F2B1B7; }
.ref-skeleton { height: 112px; border-radius: 16px; background: linear-gradient(90deg, rgba(255,255,255,.04), rgba(255,255,255,.09), rgba(255,255,255,.04)); background-size: 200% 100%; animation: ref-shimmer 1.2s ease-in-out infinite; }

.ref-dialog {
  width: min(560px, calc(100vw - 32px)); max-width: 560px !important; max-height: min(88vh, 720px);
  padding: 0 !important; display: flex; flex-direction: column; overflow: hidden;
  color: __TEXT_PRIMARY__; background: __SURFACE__ !important; border: 1px solid __BORDER__; border-radius: 18px !important;
  font-family: __FONT__;
}
.ref-dialog-body { position: relative; padding: 24px 24px 8px; overflow-y: auto; }
.ref-dialog-title { margin: 0 44px 18px 0 !important; font-size: 21px !important; font-weight: 800 !important; }
.ref-close {
  position: absolute; top: 14px; right: 14px; width: 44px; height: 44px; display: grid; place-items: center;
  border: 0; border-radius: 10px; color: __TEXT_SECONDARY__; background: transparent; cursor: pointer;
}
.ref-close:hover { color: __TEXT_PRIMARY__; background: rgba(255,255,255,.06); }
.ref-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.ref-field { display: grid; gap: 7px; min-width: 0; margin-bottom: 14px; }
.ref-label { color: #E8EEF8; font-size: 13px; font-weight: 650; }
.ref-input, .ref-select {
  width: 100%; min-height: 44px; padding: 0 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 10px;
  color: __TEXT_PRIMARY__; background: rgba(5,12,24,.54); font: inherit; font-size: 14.5px; color-scheme: dark;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
.ref-select { justify-content: space-between; box-shadow: none !important; }
textarea.ref-input { min-height: 120px; padding: 12px; resize: vertical; line-height: 1.5; }
.ref-input:focus, .ref-select:focus, .ref-select[data-state="open"] { outline: none; border-color: __PRIMARY__; box-shadow: 0 0 0 3px rgba(43,140,255,.18) !important; }
.ref-input[aria-invalid="true"], .ref-select[aria-invalid="true"] { border-color: #D6818B; }
.ref-counter { justify-self: end; color: __TEXT_MUTED__; font-size: 12px; }
.ref-error-text { margin: 0; color: #F0A1A9; font-size: 12.5px; line-height: 1.4; }
.ref-global-error { margin: 0 0 12px; padding: 10px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px; color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px; }
.ref-dialog-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 24px 20px; border-top: 1px solid rgba(255,255,255,.06); background: __SURFACE__; }
.ref-select-content { background: #142238 !important; border: 1px solid rgba(255,255,255,.1); }
.ref-select-content [role="option"] { min-height: 40px; color: __TEXT_PRIMARY__; font-size: 14px; }
.ref-select-content [role="option"][data-highlighted] { background: rgba(43,140,255,.18) !important; color: #FFFFFF !important; }
.ref-select-content [role="option"][data-state="checked"] { background: rgba(43,140,255,.12); color: #BFDAFF; }
.ref-select-content [role="option"] svg { color: __PRIMARY__; }
.ref-alert { max-width: 420px !important; color: __TEXT_PRIMARY__; background: __SURFACE__ !important; border: 1px solid __BORDER__; border-radius: 16px !important; font-family: __FONT__; }
.ref-alert-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }

.rt-DialogOverlay, .rt-AlertDialogOverlay { background: rgba(3,8,18,.72) !important; }
.ref-dialog, .ref-alert { animation: ref-pop 180ms cubic-bezier(.2,.8,.2,1) both; }

@keyframes ref-fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes ref-pop { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }
@keyframes ref-shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }

@media (max-width: 900px) {
  .ref-totals { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .ref-header { flex-direction: column; align-items: stretch; }
  .ref-header .ref-button { width: 100%; }
  .ref-title { font-size: 27px; }
  .ref-total { padding: 14px 16px; }
  .ref-total-value { font-size: 23px; }
  .ref-form-grid { grid-template-columns: minmax(0, 1fr); gap: 0; }
  .ref-dialog { width: calc(100vw - 16px); max-height: calc(100dvh - 24px); }
  .ref-dialog-body { padding: 20px 16px 8px; }
  .ref-dialog-footer { padding: 12px 16px 16px; }
  .ref-dialog-footer .ref-button { flex: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .ref-item, .ref-dialog, .ref-alert, .ref-skeleton { animation: none !important; }
  .ref-total:hover, .ref-item:hover { transform: none; }
}
""")


def page_header() -> rx.Component:
    return rx.el.header(
        rx.box(
            rx.box(
                rx.box(rx.icon(tag="utensils", size=20, aria_hidden="true"), class_name="ref-header-icon"),
                rx.el.h1("Refeições", class_name="ref-title"),
                class_name="ref-header-row",
            ),
            rx.el.p(
                "Descreva o que você comeu. Em breve a IA estimará calorias e macronutrientes automaticamente.",
                class_name="ref-subtitle",
            ),
        ),
        rx.dialog.trigger(
            rx.el.button(
                rx.icon(tag="plus", size=18, aria_hidden="true"),
                "Nova refeição",
                type="button",
                title="Abre o formulário para registrar uma refeição",
                on_click=RefeicoesState.open_new_meal,
                class_name="ref-button",
            ),
        ),
        class_name="ref-header",
    )


def total_card(rotulo: str, valor, unidade: str) -> rx.Component:
    return rx.box(
        rx.el.p(rotulo, class_name="ref-total-label"),
        rx.el.p(valor, rx.el.span(unidade, class_name="ref-total-unit"), class_name="ref-total-value"),
        class_name="ref-total",
    )


def daily_totals() -> rx.Component:
    return rx.el.section(
        rx.box(
            total_card("Calorias hoje", RefeicoesState.total_calorias, "kcal"),
            total_card("Proteínas", RefeicoesState.total_proteinas, "g"),
            total_card("Carboidratos", RefeicoesState.total_carboidratos, "g"),
            total_card("Gorduras", RefeicoesState.total_gorduras, "g"),
            class_name="ref-totals",
        ),
        rx.cond(
            RefeicoesState.pendentes_hoje > 0,
            rx.el.p(
                f"{RefeicoesState.pendentes_hoje} refeição(ões) aguardando análise da IA",
                class_name="ref-pending-note",
            ),
            rx.fragment(),
        ),
        aria_label="Totais de hoje",
    )


def meal_item(refeicao) -> rx.Component:
    analisada = refeicao["analisada"] != ""
    return rx.el.li(
        rx.box(
            rx.el.span(refeicao["tipo"], class_name="ref-chip"),
            rx.el.span(refeicao["data"], class_name="ref-date"),
            rx.cond(analisada, rx.el.span(refeicao["calorias"], class_name="ref-calories"), rx.fragment()),
            rx.el.button(
                rx.icon(tag="trash-2", size=18, aria_hidden="true"),
                type="button",
                aria_label=f"Excluir refeição: {refeicao['tipo']} de {refeicao['data']}",
                title="Excluir esta refeição",
                on_click=RefeicoesState.ask_delete(refeicao["id"]),
                class_name="ref-delete",
            ),
            class_name="ref-item-top",
        ),
        rx.el.p(refeicao["descricao"], class_name="ref-description"),
        rx.cond(
            analisada,
            rx.el.p(refeicao["macros"], class_name="ref-macros"),
            rx.el.span(
                rx.icon(tag="hourglass", size=13, aria_hidden="true"),
                "Aguardando análise",
                class_name="ref-pending-badge",
            ),
        ),
        class_name="ref-item",
    )


def empty_state() -> rx.Component:
    return rx.box(
        rx.box(rx.icon(tag="utensils", size=22, aria_hidden="true"), class_name="ref-header-icon"),
        rx.el.p("Nenhuma refeição registrada", class_name="ref-empty-title"),
        rx.el.p("Descreva sua primeira refeição para começar o seu histórico.", class_name="ref-empty-text"),
        class_name="ref-empty",
    )


def list_error() -> rx.Component:
    return rx.box(
        rx.el.p(RefeicoesState.erro_lista, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            title="Busca suas refeições de novo",
            on_click=RefeicoesState.start_page,
            class_name="ref-button-secondary",
        ),
        class_name="ref-error",
    )


def meal_list() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Histórico", id="ref-historico-titulo", class_name="ref-list-title"),
        rx.cond(
            RefeicoesState.carregando,
            rx.box(
                rx.box(class_name="ref-skeleton"),
                rx.box(class_name="ref-skeleton"),
                class_name="ref-list",
                aria_busy="true",
                aria_label="Carregando refeições",
            ),
            rx.cond(
                RefeicoesState.erro_lista != "",
                list_error(),
                rx.cond(
                    RefeicoesState.refeicoes.length() == 0,
                    empty_state(),
                    rx.el.ul(rx.foreach(RefeicoesState.refeicoes, meal_item), class_name="ref-list"),
                ),
            ),
        ),
        aria_labelledby="ref-historico-titulo",
        class_name="ref-list-section",
    )


def field_error(campo: str, input_id: str) -> rx.Component:
    return rx.el.p(
        RefeicoesState.erros.get(campo, ""),
        id=f"{input_id}-erro",
        aria_live="polite",
        class_name="ref-error-text",
    )


def new_meal_form() -> rx.Component:
    return rx.box(
        rx.dialog.title("Nova refeição", id="ref-modal-titulo", class_name="ref-dialog-title"),
        rx.box(
            rx.box(
                rx.el.label("Data", html_for="ref-data", class_name="ref-label"),
                rx.el.input(
                    id="ref-data",
                    type="date",
                    name="data_refeicao",
                    value=RefeicoesState.data_refeicao,
                    max=RefeicoesState.hoje,
                    on_change=lambda valor: RefeicoesState.update_field("data_refeicao", valor),
                    aria_invalid=RefeicoesState.erros.contains("data_refeicao"),
                    aria_describedby="ref-data-erro",
                    class_name="ref-input",
                ),
                field_error("data_refeicao", "ref-data"),
                class_name="ref-field",
            ),
            rx.box(
                rx.el.label("Tipo", html_for="ref-tipo", class_name="ref-label"),
                rx.select.root(
                    rx.select.trigger(
                        id="ref-tipo",
                        placeholder="Selecione",
                        aria_invalid=RefeicoesState.erros.contains("tipo"),
                        aria_describedby="ref-tipo-erro",
                        class_name="ref-select",
                    ),
                    rx.select.content(
                        *[rx.select.item(opcao, value=opcao) for opcao in OPCOES_TIPO],
                        position="popper",
                        variant="soft",
                        class_name="ref-select-content",
                    ),
                    value=RefeicoesState.tipo,
                    on_change=lambda valor: RefeicoesState.update_field("tipo", valor),
                    name="tipo",
                ),
                field_error("tipo", "ref-tipo"),
                class_name="ref-field",
            ),
            class_name="ref-form-grid",
        ),
        rx.box(
            rx.el.label("Descrição", html_for="ref-descricao", class_name="ref-label"),
            rx.el.textarea(
                id="ref-descricao",
                name="descricao",
                value=RefeicoesState.descricao,
                rows=5,
                max_length=TAMANHO_MAXIMO_DESCRICAO,
                placeholder="Ex.: 2 ovos mexidos, 1 fatia de pão integral, 1 banana e café sem açúcar",
                on_change=lambda valor: RefeicoesState.update_field("descricao", valor),
                aria_invalid=RefeicoesState.erros.contains("descricao"),
                aria_describedby="ref-descricao-erro ref-descricao-contador",
                class_name="ref-input",
            ),
            rx.el.span(
                f"{RefeicoesState.descricao.length()}/{TAMANHO_MAXIMO_DESCRICAO}",
                id="ref-descricao-contador",
                class_name="ref-counter",
            ),
            field_error("descricao", "ref-descricao"),
            class_name="ref-field",
        ),
        rx.cond(
            RefeicoesState.erro_geral != "",
            rx.el.p(RefeicoesState.erro_geral, role="status", aria_live="polite", class_name="ref-global-error"),
            rx.fragment(),
        ),
        # o X fica depois dos campos no DOM: o foco inicial do modal cai no primeiro campo
        rx.dialog.close(
            rx.el.button(
                rx.icon(tag="x", size=20, aria_hidden="true"),
                type="button",
                aria_label="Fechar",
                title="Fechar sem perder o que já foi digitado",
                class_name="ref-close",
            ),
        ),
        class_name="ref-dialog-body",
    )


def new_meal_footer() -> rx.Component:
    return rx.box(
        rx.el.button(
            rx.cond(
                RefeicoesState.salvando,
                rx.spinner(size="2"),
                rx.icon(tag="save", size=17, aria_hidden="true"),
            ),
            "Salvar",
            type="button",
            title="Registra a refeição no seu histórico",
            on_click=RefeicoesState.save_meal,
            disabled=RefeicoesState.salvando,
            aria_busy=RefeicoesState.salvando,
            class_name="ref-button",
        ),
        class_name="ref-dialog-footer",
    )


def delete_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Excluir esta refeição?"),
            rx.alert_dialog.description("Ela sai do seu histórico e dos totais do dia. Essa ação não pode ser desfeita."),
            rx.box(
                rx.alert_dialog.cancel(
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        title="Mantém a refeição",
                        class_name="ref-button-secondary",
                    ),
                ),
                rx.el.button(
                    rx.cond(RefeicoesState.excluindo, rx.spinner(size="2"), rx.icon(tag="trash-2", size=16, aria_hidden="true")),
                    "Excluir",
                    type="button",
                    title="Exclui a refeição definitivamente",
                    on_click=RefeicoesState.confirm_delete,
                    disabled=RefeicoesState.excluindo,
                    class_name="ref-button ref-button-danger",
                ),
                class_name="ref-alert-actions",
            ),
            class_name="ref-alert",
        ),
        open=RefeicoesState.exclusao_id != "",
        on_open_change=RefeicoesState.set_delete_open,
    )


def refeicoes_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(
            rx.dialog.root(
                page_header(),
                rx.dialog.content(
                    new_meal_form(),
                    new_meal_footer(),
                    aria_labelledby="ref-modal-titulo",
                    aria_describedby=None,
                    class_name="ref-dialog",
                ),
                open=RefeicoesState.modal_aberto,
                on_open_change=RefeicoesState.set_modal_open,
            ),
            daily_totals(),
            meal_list(),
            delete_dialog(),
            class_name="ref-page",
        ),
        REFEICOES_PAGE_CSS,
    )
