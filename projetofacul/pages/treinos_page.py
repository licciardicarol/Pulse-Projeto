"""Tela /treinos: cabeçalho, histórico de treinos, modal "Novo treino", exclusão e estados vazio/carregando/erro."""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.logic.treinos import (
    DURACAO_MAXIMA,
    DURACAO_MINIMA,
    TAMANHO_MAXIMO_CATEGORIA,
    TAMANHO_MAXIMO_INTENSIDADE,
    TAMANHO_MAXIMO_NOME,
    TAMANHO_MAXIMO_OBSERVACOES,
)
from projetofacul.states.treinos_state import TreinosState
from styles.theme import apply_theme_tokens

ROTA = "/treinos"

SUBTITULO = "Registre suas sessões de treino e acompanhe seu histórico."

ID_BOTAO_NOVO_TREINO = "trn-novo-treino"

# o Radix não reconhece o botão como gatilho (abertura controlada pelo State), então o foco
# voltaria para o <body> ao fechar; devolvemos o foco ao botão "Novo treino" explicitamente
RETORNAR_FOCO = [
    rx.prevent_default,
    rx.call_script(f"document.getElementById('{ID_BOTAO_NOVO_TREINO}')?.focus()"),
]

TREINOS_PAGE_CSS = apply_theme_tokens("""
.trn-page { width: min(1200px, 100%); margin: 0 auto; }
.trn-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 28px; }
.trn-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.trn-icon {
  width: 44px; height: 44px; flex: none; display: grid; place-items: center; border-radius: 12px;
  color: __PRIMARY__; background: rgba(43,140,255,.14);
}
.trn-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.trn-subtitle { margin: 0; max-width: 640px; color: __TEXT_SECONDARY__; font-size: 15.5px; line-height: 1.6; }
.trn-button {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 20px;
  border: 0; border-radius: 10px; color: #FFFFFF; background: __PRIMARY__; font: inherit; font-size: 14.5px;
  font-weight: 700; white-space: nowrap; cursor: pointer; box-shadow: 0 10px 24px rgba(43,140,255,.18);
  transition: transform 170ms ease, box-shadow 170ms ease, background 170ms ease, opacity 170ms ease;
}
.trn-button:hover:not(:disabled) { transform: translateY(-1px); background: __PRIMARY_HOVER__; box-shadow: 0 14px 30px rgba(43,140,255,.26); }
.trn-button:active:not(:disabled) { transform: scale(.98); }
.trn-button:disabled { opacity: .72; cursor: wait; }
.trn-button-secondary {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 18px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.trn-button-secondary:hover { background: rgba(255,255,255,.06); }
.trn-button-secondary:active { transform: scale(.98); }
.trn-button:focus-visible, .trn-button-secondary:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }

.trn-list { display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }
.trn-empty {
  display: grid; justify-items: center; gap: 10px; padding: 56px 24px; border: 1.5px dashed rgba(255,255,255,.16);
  border-radius: 18px; text-align: center;
}
.trn-empty-title { margin: 6px 0 0; font-size: 18px; font-weight: 800; }
.trn-empty-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; }
.trn-error {
  display: grid; justify-items: center; gap: 12px; padding: 32px 24px; border: 1px solid rgba(240,161,169,.24);
  border-radius: 16px; background: rgba(130,35,48,.12); text-align: center;
}
.trn-error p { margin: 0; color: #F2B1B7; }
.trn-skeleton {
  height: 112px; border-radius: 16px;
  background: linear-gradient(90deg, rgba(255,255,255,.04), rgba(255,255,255,.09), rgba(255,255,255,.04));
  background-size: 200% 100%; animation: trn-shimmer 1.2s ease-in-out infinite;
}

.trn-dialog {
  width: min(560px, calc(100vw - 32px)); max-width: 560px !important; max-height: min(88vh, 760px);
  padding: 0 !important; display: flex; flex-direction: column; overflow: hidden;
  color: __TEXT_PRIMARY__; background: __SURFACE__ !important; border: 1px solid __BORDER__; border-radius: 18px !important;
  font-family: __FONT__; animation: trn-pop 180ms cubic-bezier(.2,.8,.2,1) both;
}
.trn-dialog-body { position: relative; padding: 24px 24px 8px; overflow-y: auto; }
.trn-dialog-title { margin: 0 44px 18px 0 !important; font-size: 21px !important; font-weight: 800 !important; }
.trn-close {
  position: absolute; top: 14px; right: 14px; width: 44px; height: 44px; display: grid; place-items: center;
  border: 0; border-radius: 10px; color: __TEXT_SECONDARY__; background: transparent; cursor: pointer;
}
.trn-close:hover { color: __TEXT_PRIMARY__; background: rgba(255,255,255,.06); }
.trn-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 14px; }
.trn-field { display: grid; gap: 7px; min-width: 0; margin-bottom: 14px; align-content: start; }
.trn-field-full { grid-column: 1 / -1; }
.trn-label { color: #FFFFFF; font-size: 13px; font-weight: 700; }
.trn-input {
  width: 100%; min-height: 44px; padding: 0 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 10px;
  color: __TEXT_PRIMARY__; background: rgba(5,12,24,.54); font: inherit; font-size: 14.5px; color-scheme: dark;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}
.trn-input::placeholder { color: __TEXT_MUTED__; }
textarea.trn-input { min-height: 104px; padding: 12px; resize: vertical; line-height: 1.5; }
.trn-input:focus { outline: none; border-color: __PRIMARY__; box-shadow: 0 0 0 3px rgba(43,140,255,.18); }
.trn-input[aria-invalid="true"] { border-color: #D6818B; }
.trn-counter { justify-self: end; color: __TEXT_MUTED__; font-size: 12px; }
.trn-error-text { margin: 0; color: #F0A1A9; font-size: 12.5px; line-height: 1.4; }
.trn-error-text:empty { display: none; }
.trn-global-error {
  margin: 0 0 12px; padding: 10px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px;
  color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px;
}
.trn-dialog-footer .trn-global-error { flex-basis: 100%; }
.trn-dialog-footer {
  display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; padding: 14px 24px 20px;
  border-top: 1px solid rgba(255,255,255,.06); background: __SURFACE__;
}
.trn-close:focus-visible, .trn-input:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
.rt-DialogOverlay, .rt-AlertDialogOverlay { background: rgba(3,8,18,.72) !important; }

.trn-item {
  display: flex; align-items: flex-start; gap: 14px; padding: 18px 20px;
  border: 1px solid __BORDER__; border-radius: 16px; background: __SURFACE__;
  transition: border-color 170ms ease, transform 170ms ease, box-shadow 170ms ease;
  animation: trn-fade-in 260ms ease both;
}
.trn-item:hover { border-color: rgba(59,147,255,.35); transform: translateY(-2px); box-shadow: 0 14px 34px rgba(0,0,0,.22); }
.trn-item-body { flex: 1; min-width: 0; }
.trn-item-name { margin: 0 0 8px; font-size: 16.5px; font-weight: 800; line-height: 1.35; overflow-wrap: anywhere; }
.trn-item-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.trn-meta-text { display: inline-flex; align-items: center; gap: 5px; color: __TEXT_SECONDARY__; font-size: 13px; }
.trn-chip {
  display: inline-flex; align-items: center; min-height: 26px; padding: 0 10px; border-radius: 999px;
  color: #8EBEFF; background: rgba(43,140,255,.14); font-size: 12.5px; font-weight: 700; overflow-wrap: anywhere;
}
.trn-chip-intensity { color: __WARNING__; background: rgba(251,191,36,.12); }
.trn-item-notes { margin: 10px 0 0; color: __TEXT_SECONDARY__; font-size: 14px; line-height: 1.55; white-space: pre-line; overflow-wrap: anywhere; }
.trn-delete {
  width: 44px; height: 44px; flex: none; display: grid; place-items: center; border: 0; border-radius: 10px;
  color: #F0707F; background: transparent; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.trn-delete:hover { background: rgba(240,112,127,.12); }
.trn-delete:active { transform: scale(.96); }
.trn-delete:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
.trn-button-danger { background: #D9475A; box-shadow: none; }
.trn-button-danger:hover:not(:disabled) { background: #E35D6F; box-shadow: none; }
.trn-alert {
  max-width: 420px !important; color: __TEXT_PRIMARY__; background: __SURFACE__ !important;
  border: 1px solid __BORDER__; border-radius: 16px !important; font-family: __FONT__;
  animation: trn-pop 180ms cubic-bezier(.2,.8,.2,1) both;
}
.trn-alert-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }

@keyframes trn-fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes trn-shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
@keyframes trn-pop { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }

@media (max-width: 640px) {
  .trn-header { flex-direction: column; align-items: stretch; }
  .trn-header .trn-button { width: 100%; }
  .trn-title { font-size: 27px; }
  .trn-form-grid { grid-template-columns: minmax(0, 1fr); }
  .trn-dialog { width: calc(100vw - 16px); max-height: calc(100dvh - 24px); }
  .trn-dialog-body { padding: 20px 16px 8px; }
  .trn-dialog-footer { padding: 12px 16px 16px; }
  .trn-dialog-footer .trn-button { flex: 1; }
  .trn-item { padding: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  .trn-skeleton, .trn-dialog, .trn-item, .trn-alert { animation: none !important; }
  .trn-item:hover { transform: none; }
}
""")


def page_header() -> rx.Component:
    return rx.el.header(
        rx.box(
            rx.box(
                rx.box(rx.icon(tag="dumbbell", size=22, aria_hidden="true"), class_name="trn-icon"),
                rx.el.h1("Treinos", class_name="trn-title"),
                class_name="trn-header-row",
            ),
            rx.el.p(SUBTITULO, class_name="trn-subtitle"),
        ),
        rx.dialog.trigger(
            rx.el.button(
                rx.icon(tag="plus", size=18, aria_hidden="true"),
                "Novo treino",
                id=ID_BOTAO_NOVO_TREINO,
                type="button",
                title="Abre o formulário para registrar um treino",
                on_click=TreinosState.open_new_workout,
                class_name="trn-button",
            ),
        ),
        class_name="trn-header",
    )


def empty_state() -> rx.Component:
    return rx.box(
        rx.box(rx.icon(tag="dumbbell", size=22, aria_hidden="true"), class_name="trn-icon"),
        rx.el.p("Nenhum treino ainda", class_name="trn-empty-title"),
        rx.el.p('Toque em "Novo treino" para registrar sua primeira sessão.', class_name="trn-empty-text"),
        class_name="trn-empty",
    )


def list_error() -> rx.Component:
    return rx.box(
        rx.el.p(TreinosState.erro_lista, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            title="Busca seus treinos de novo",
            on_click=TreinosState.start_page,
            class_name="trn-button-secondary",
        ),
        class_name="trn-error",
    )


def field_error(campo: str, input_id: str) -> rx.Component:
    return rx.el.p(
        TreinosState.erros.get(campo, ""),
        id=f"{input_id}-erro",
        aria_live="polite",
        class_name="trn-error-text",
    )


def text_field(campo: str, rotulo: str, placeholder: str, limite: int, largura_total: bool = False) -> rx.Component:
    input_id = f"trn-{campo}"
    return rx.box(
        rx.el.label(rotulo, html_for=input_id, class_name="trn-label"),
        rx.el.input(
            id=input_id,
            type="text",
            name=campo,
            value=getattr(TreinosState, campo),
            placeholder=placeholder,
            max_length=limite,
            on_change=lambda valor: TreinosState.update_field(campo, valor),
            aria_invalid=TreinosState.erros.contains(campo),
            aria_describedby=f"{input_id}-erro",
            class_name="trn-input",
        ),
        field_error(campo, input_id),
        class_name="trn-field trn-field-full" if largura_total else "trn-field",
    )


def new_workout_form() -> rx.Component:
    return rx.box(
        rx.dialog.title("Novo treino", id="trn-modal-titulo", class_name="trn-dialog-title"),
        rx.box(
            # linha 1: Data e Duração
            rx.box(
                rx.el.label("Data", html_for="trn-data", class_name="trn-label"),
                rx.el.input(
                    id="trn-data",
                    type="date",
                    name="data",
                    value=TreinosState.data,
                    # o navegador exibe dd/mm/aaaa em pt-BR; o limite é "hoje" em São Paulo
                    max=TreinosState.hoje,
                    on_change=lambda valor: TreinosState.update_field("data", valor),
                    aria_invalid=TreinosState.erros.contains("data"),
                    aria_describedby="trn-data-erro",
                    class_name="trn-input",
                ),
                field_error("data", "trn-data"),
                class_name="trn-field",
            ),
            rx.box(
                rx.el.label("Duração (min)", html_for="trn-duracao_minutos", class_name="trn-label"),
                rx.el.input(
                    id="trn-duracao_minutos",
                    type="number",
                    name="duracao_minutos",
                    value=TreinosState.duracao_minutos,
                    min=DURACAO_MINIMA,
                    max=DURACAO_MAXIMA,
                    step=1,
                    input_mode="numeric",
                    placeholder="Ex.: 60",
                    on_change=lambda valor: TreinosState.update_field("duracao_minutos", valor),
                    aria_invalid=TreinosState.erros.contains("duracao_minutos"),
                    aria_describedby="trn-duracao_minutos-erro",
                    class_name="trn-input",
                ),
                field_error("duracao_minutos", "trn-duracao_minutos"),
                class_name="trn-field",
            ),
            # linha 2: Nome (linha inteira)
            text_field("nome", "Nome", "Ex.: Peito e tríceps", TAMANHO_MAXIMO_NOME, largura_total=True),
            # linha 3: Categoria e Intensidade (texto livre, como no Xano)
            text_field("categoria", "Categoria", "Musculação, corrida...", TAMANHO_MAXIMO_CATEGORIA),
            text_field("intensidade", "Intensidade", "Leve, moderada, alta", TAMANHO_MAXIMO_INTENSIDADE),
            # linha 4: Observações (linha inteira)
            rx.box(
                rx.el.label("Observações", html_for="trn-observacoes", class_name="trn-label"),
                rx.el.textarea(
                    id="trn-observacoes",
                    name="observacoes",
                    value=TreinosState.observacoes,
                    rows=4,
                    max_length=TAMANHO_MAXIMO_OBSERVACOES,
                    placeholder="Como foi o treino?",
                    on_change=lambda valor: TreinosState.update_field("observacoes", valor),
                    aria_invalid=TreinosState.erros.contains("observacoes"),
                    aria_describedby="trn-observacoes-erro trn-observacoes-contador",
                    class_name="trn-input",
                ),
                rx.el.span(
                    f"{TreinosState.observacoes.length()}/{TAMANHO_MAXIMO_OBSERVACOES}",
                    id="trn-observacoes-contador",
                    class_name="trn-counter",
                ),
                field_error("observacoes", "trn-observacoes"),
                class_name="trn-field trn-field-full",
            ),
            class_name="trn-form-grid",
        ),
        # o X fica depois dos campos no DOM: o foco inicial do modal cai no primeiro campo (Data)
        rx.dialog.close(
            rx.el.button(
                rx.icon(tag="x", size=20, aria_hidden="true"),
                type="button",
                aria_label="Fechar",
                title="Fechar sem perder o que já foi digitado",
                class_name="trn-close",
            ),
        ),
        class_name="trn-dialog-body",
    )


def new_workout_footer() -> rx.Component:
    # fora da área com rolagem: o botão fica sempre visível no celular
    return rx.box(
        rx.cond(
            TreinosState.erro_geral != "",
            rx.el.p(TreinosState.erro_geral, role="status", aria_live="polite", class_name="trn-global-error"),
            rx.fragment(),
        ),
        rx.el.button(
            rx.cond(TreinosState.salvando, rx.spinner(size="2"), rx.icon(tag="save", size=17, aria_hidden="true")),
            "Salvar treino",
            type="button",
            title="Registra o treino no seu histórico",
            on_click=TreinosState.save_workout,
            disabled=TreinosState.salvando,
            aria_busy=TreinosState.salvando,
            class_name="trn-button",
        ),
        class_name="trn-dialog-footer",
    )


def workout_item(treino) -> rx.Component:
    # campos opcionais vazios simplesmente não aparecem (sem placeholders falsos)
    return rx.el.li(
        rx.box(
            rx.el.h3(treino["nome"], class_name="trn-item-name"),
            rx.box(
                rx.el.span(
                    rx.icon(tag="calendar", size=14, aria_hidden="true"), treino["data"], class_name="trn-meta-text"
                ),
                rx.cond(
                    treino["duracao"] != "",
                    rx.el.span(
                        rx.icon(tag="clock", size=14, aria_hidden="true"), treino["duracao"], class_name="trn-meta-text"
                    ),
                    rx.fragment(),
                ),
                rx.cond(treino["categoria"] != "", rx.el.span(treino["categoria"], class_name="trn-chip"), rx.fragment()),
                rx.cond(
                    treino["intensidade"] != "",
                    rx.el.span(treino["intensidade"], class_name="trn-chip trn-chip-intensity"),
                    rx.fragment(),
                ),
                class_name="trn-item-meta",
            ),
            rx.cond(treino["observacoes"] != "", rx.el.p(treino["observacoes"], class_name="trn-item-notes"), rx.fragment()),
            class_name="trn-item-body",
        ),
        rx.el.button(
            rx.icon(tag="trash-2", size=18, aria_hidden="true"),
            type="button",
            aria_label=f"Excluir treino {treino['nome']}",
            title="Excluir este treino",
            on_click=TreinosState.ask_delete(treino["id"], treino["nome"]),
            class_name="trn-delete",
        ),
        class_name="trn-item",
    )


def delete_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Excluir este treino?"),
            rx.alert_dialog.description("Ele sai do seu histórico. Essa ação não pode ser desfeita."),
            rx.box(
                rx.alert_dialog.cancel(
                    rx.el.button("Cancelar", type="button", title="Mantém o treino", class_name="trn-button-secondary"),
                ),
                rx.el.button(
                    rx.cond(
                        TreinosState.excluindo, rx.spinner(size="2"), rx.icon(tag="trash-2", size=16, aria_hidden="true")
                    ),
                    "Excluir",
                    type="button",
                    title="Exclui o treino definitivamente",
                    on_click=TreinosState.confirm_delete,
                    disabled=TreinosState.excluindo,
                    class_name="trn-button trn-button-danger",
                ),
                class_name="trn-alert-actions",
            ),
            # depois de excluir o card some; o foco vai para um ponto estável da página
            on_close_auto_focus=RETORNAR_FOCO,
            class_name="trn-alert",
        ),
        open=TreinosState.exclusao_id != "",
        on_open_change=TreinosState.set_delete_open,
    )


def workout_list() -> rx.Component:
    return rx.el.section(
        rx.cond(
            TreinosState.carregando,
            rx.box(
                rx.box(class_name="trn-skeleton"),
                rx.box(class_name="trn-skeleton"),
                rx.box(class_name="trn-skeleton"),
                class_name="trn-list",
                aria_busy="true",
                aria_label="Carregando treinos",
            ),
            rx.cond(
                TreinosState.erro_lista != "",
                list_error(),
                rx.cond(
                    TreinosState.treinos.length() == 0,
                    empty_state(),
                    rx.el.ul(rx.foreach(TreinosState.treinos, workout_item), class_name="trn-list"),
                ),
            ),
        ),
        aria_label="Histórico de treinos",
    )


def treinos_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(
            rx.dialog.root(
                page_header(),
                rx.dialog.content(
                    new_workout_form(),
                    new_workout_footer(),
                    aria_labelledby="trn-modal-titulo",
                    aria_describedby=None,
                    on_close_auto_focus=RETORNAR_FOCO,
                    class_name="trn-dialog",
                ),
                open=TreinosState.modal_aberto,
                on_open_change=TreinosState.set_modal_open,
            ),
            workout_list(),
            delete_dialog(),
            class_name="trn-page",
        ),
        TREINOS_PAGE_CSS,
    )
