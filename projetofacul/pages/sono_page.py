"""Tela /sono: formulário em card, duração ao vivo, histórico, edição e exclusão.

Usa o CSS de Refeições (classes `ref-*`) para seguir o mesmo padrão visual; aqui
fica só o que Refeições não tem: card do formulário, chips de qualidade, rodapé
com a duração e o botão de editar.
"""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.logic.sono_registro import OPCOES_QUALIDADE, TAMANHO_MAXIMO_OBSERVACOES
from projetofacul.pages.refeicoes_page import REFEICOES_PAGE_CSS
from projetofacul.states.sono_state import SonoState
from styles.theme import apply_theme_tokens

ROTA = "/sono"

SUBTITULO = (
    "Registre início, fim e qualidade do sono. Esses dados alimentam as recomendações "
    "de recuperação e de intensidade de treino."
)

SONO_PAGE_CSS = apply_theme_tokens("""
.sono-card {
  padding: 22px 24px 0; border: 1px solid __BORDER__; border-radius: 16px; background: __SURFACE__;
  scroll-margin-top: 80px;
}
.sono-card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.sono-timezone-note { margin: -8px 0 16px; color: __TEXT_MUTED__; font-size: 13px; }
.sono-card input[type="datetime-local"] { cursor: pointer; }
.sono-card .ref-field { margin-bottom: 6px; }
/* espaço reservado para a mensagem: o erro aparece sem empurrar o layout */
.sono-card .ref-error-text { min-height: 18px; }
.sono-fieldset { min-width: 0; margin: 0 0 6px; padding: 0; border: 0; }
.sono-fieldset legend { padding: 0; margin-bottom: 7px; }
.sono-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 7px; }
.sono-chip {
  min-height: 36px; display: inline-flex; align-items: center; gap: 7px; padding: 0 12px;
  border: 1px solid rgba(255,255,255,.12); border-radius: 999px; color: __TEXT_SECONDARY__; background: transparent;
  font: inherit; font-size: 14px; cursor: pointer;
  transition: border-color 150ms ease, color 150ms ease, background 150ms ease, transform 150ms ease;
}
.sono-chip:hover { border-color: rgba(59,147,255,.4); color: __TEXT_PRIMARY__; }
.sono-chip:active { transform: scale(.97); }
.sono-chip.is-active { border-color: __PRIMARY__; color: __TEXT_PRIMARY__; background: rgba(43,140,255,.16); }
.sono-chip-number { font-weight: 700; }
.sono-star { color: __TEXT_MUTED__; flex: none; }
.sono-chip.is-active .sono-star, .sono-star.is-filled { color: __PRIMARY__; fill: currentColor; }
.sono-card-footer {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  margin: 8px -24px 0; padding: 14px 24px 20px; border-top: 1px solid rgba(255,255,255,.06);
}
.sono-duration { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; }
.sono-duration strong { color: __TEXT_PRIMARY__; font-size: 16px; font-weight: 700; }
.sono-actions { display: flex; gap: 10px; }
.sono-card .ref-button:disabled:not([aria-busy="true"]) { cursor: not-allowed; box-shadow: none; }
.sono-save-error { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 4px; }
.sono-save-error .ref-global-error { flex: 1 1 260px; margin: 0; }
.sono-rating { display: inline-flex; align-items: center; gap: 3px; margin-top: 8px; color: __TEXT_SECONDARY__; font-size: 13.5px; }
.sono-rating-label { margin-left: 6px; }
.sono-edit {
  width: 44px; height: 44px; display: grid; place-items: center; margin-left: auto; border: 0; border-radius: 10px;
  color: __TEXT_SECONDARY__; background: transparent; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.sono-edit:hover { color: __TEXT_PRIMARY__; background: rgba(255,255,255,.06); }
.sono-edit:active { transform: scale(.96); }
.ref-item-top .sono-edit + .ref-delete { margin-left: 0; }
.sono-chip:focus-visible, .sono-edit:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
@media (pointer: coarse) {
  .sono-chip { min-height: 44px; }
}
@media (max-width: 640px) {
  .sono-card { padding: 18px 16px 0; }
  .sono-card-footer { flex-direction: column; align-items: stretch; margin: 8px -16px 0; padding: 12px 16px 16px; }
  .sono-actions { flex-direction: column-reverse; }
  .sono-actions .ref-button, .sono-actions .ref-button-secondary { width: 100%; }
}
""")


def page_header() -> rx.Component:
    return rx.el.header(
        rx.box(
            rx.box(
                rx.box(rx.icon(tag="moon", size=20, aria_hidden="true"), class_name="ref-header-icon"),
                rx.el.h1("Sono", class_name="ref-title"),
                class_name="ref-header-row",
            ),
            rx.el.p(SUBTITULO, class_name="ref-subtitle"),
        ),
        class_name="ref-header",
    )


def field_error(campo: str, input_id: str) -> rx.Component:
    return rx.el.p(
        SonoState.erros.get(campo, ""),
        id=f"{input_id}-erro",
        aria_live="polite",
        class_name="ref-error-text",
    )


def open_picker_script(input_id: str) -> str:
    # o clique em qualquer parte do campo abre o calendário com as colunas de hora e minuto;
    # navegadores sem showPicker continuam com o campo digitável
    return f"(() => {{ try {{ document.getElementById('{input_id}').showPicker(); }} catch (e) {{}} }})()"


def datetime_field(rotulo: str, campo: str, input_id: str, valor) -> rx.Component:
    return rx.box(
        rx.el.label(rotulo, html_for=input_id, class_name="ref-label"),
        rx.el.input(
            id=input_id,
            type="datetime-local",
            name=campo,
            value=valor,
            max=SonoState.limite_maximo,
            required=True,
            on_click=rx.call_script(open_picker_script(input_id)),
            on_change=lambda texto: SonoState.update_field(campo, texto),
            aria_invalid=SonoState.erros.contains(campo),
            aria_describedby=f"{input_id}-erro",
            class_name="ref-input",
        ),
        field_error(campo, input_id),
        class_name="ref-field",
    )


def quality_chip(numero: int, rotulo: str) -> rx.Component:
    ativa = SonoState.qualidade_sono == numero
    return rx.el.button(
        rx.icon(tag="star", size=16, aria_hidden="true", class_name="sono-star"),
        rx.el.span(str(numero), class_name="sono-chip-number"),
        rx.el.span(rotulo),
        type="button",
        aria_pressed=ativa,
        title=f"Qualidade {numero} de 5: {rotulo}",
        on_click=SonoState.select_qualidade(numero),
        class_name=rx.cond(ativa, "sono-chip is-active", "sono-chip"),
    )


def quality_field() -> rx.Component:
    return rx.el.fieldset(
        rx.el.legend("Qualidade do sono", class_name="ref-label"),
        rx.box(
            *[quality_chip(numero, rotulo) for numero, rotulo in OPCOES_QUALIDADE],
            role="group",
            aria_label="Qualidade do sono, de 1 a 5",
            aria_describedby="sono-qualidade-erro",
            class_name="sono-chips",
        ),
        field_error("qualidade_sono", "sono-qualidade"),
        class_name="sono-fieldset",
    )


def notes_field() -> rx.Component:
    return rx.box(
        rx.el.label("Observações (opcional)", html_for="sono-observacoes", class_name="ref-label"),
        rx.el.textarea(
            id="sono-observacoes",
            name="observacoes",
            value=SonoState.observacoes,
            rows=4,
            max_length=TAMANHO_MAXIMO_OBSERVACOES,
            placeholder="Acordou cansado? Sonhos, interrupções, cafeína à noite…",
            on_change=lambda texto: SonoState.update_field("observacoes", texto),
            aria_invalid=SonoState.erros.contains("observacoes"),
            aria_describedby="sono-observacoes-erro sono-observacoes-contador",
            class_name="ref-input",
        ),
        rx.el.span(
            f"{SonoState.observacoes.length()}/{TAMANHO_MAXIMO_OBSERVACOES}",
            id="sono-observacoes-contador",
            class_name="ref-counter",
        ),
        field_error("observacoes", "sono-observacoes"),
        class_name="ref-field",
    )


def save_error() -> rx.Component:
    return rx.cond(
        SonoState.erro_geral != "",
        rx.box(
            rx.el.p(SonoState.erro_geral, role="status", aria_live="polite", class_name="ref-global-error"),
            rx.cond(
                SonoState.erro_permite_repetir,
                rx.el.button(
                    rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
                    "Tentar novamente",
                    type="button",
                    title="Envia o registro de novo, com os dados preenchidos",
                    on_click=SonoState.save_sono,
                    class_name="ref-button-secondary",
                ),
                rx.fragment(),
            ),
            class_name="sono-save-error",
        ),
        rx.fragment(),
    )


def form_footer() -> rx.Component:
    return rx.box(
        rx.el.p(
            "Duração: ",
            rx.el.strong(SonoState.duracao_texto),
            aria_live="polite",
            class_name="sono-duration",
        ),
        rx.box(
            rx.cond(
                SonoState.editando_id != "",
                rx.el.button(
                    "Cancelar edição",
                    type="button",
                    title="Descarta as alterações e volta ao novo registro",
                    on_click=SonoState.cancel_edit,
                    disabled=SonoState.salvando,
                    class_name="ref-button-secondary",
                ),
                rx.fragment(),
            ),
            rx.el.button(
                rx.cond(
                    SonoState.salvando,
                    rx.spinner(size="2"),
                    rx.icon(tag="save", size=17, aria_hidden="true"),
                ),
                rx.cond(SonoState.editando_id != "", "Salvar alterações", "Salvar sono"),
                type="button",
                title="Registra o período de sono no seu histórico",
                on_click=SonoState.save_sono,
                disabled=~SonoState.pode_salvar | SonoState.salvando,
                aria_busy=SonoState.salvando,
                class_name="ref-button",
            ),
            class_name="sono-actions",
        ),
        class_name="sono-card-footer",
    )


def sleep_form() -> rx.Component:
    return rx.el.section(
        rx.box(
            rx.el.h2(
                rx.cond(SonoState.editando_id != "", "Editar registro", "Novo registro"),
                id="sono-form-titulo",
                class_name="ref-list-title",
            ),
            class_name="sono-card-head",
        ),
        rx.el.p(
            "Datas e horas no horário de Brasília. O dia vira à meia-noite (00:00).",
            class_name="sono-timezone-note",
        ),
        rx.box(
            datetime_field("Início do sono", "inicio_sono", "sono-inicio", SonoState.inicio_sono),
            datetime_field("Fim do sono", "fim_sono", "sono-fim", SonoState.fim_sono),
            class_name="ref-form-grid",
        ),
        quality_field(),
        notes_field(),
        save_error(),
        form_footer(),
        id="sono-formulario",
        aria_labelledby="sono-form-titulo",
        class_name="sono-card",
    )


def rating(registro) -> rx.Component:
    qualidade = registro["qualidade"].to(int)
    return rx.box(
        *[
            rx.icon(
                tag="star",
                size=15,
                aria_hidden="true",
                class_name=rx.cond(qualidade >= numero, "sono-star is-filled", "sono-star"),
            )
            for numero in range(1, 6)
        ],
        rx.el.span(registro["rotulo_qualidade"], class_name="sono-rating-label", aria_hidden="true"),
        role="img",
        aria_label=registro["descricao_qualidade"],
        class_name="sono-rating",
    )


def record_item(registro) -> rx.Component:
    return rx.el.li(
        rx.box(
            rx.el.span(registro["duracao"], class_name="ref-chip"),
            rx.el.span(registro["data"], class_name="ref-date"),
            rx.el.button(
                rx.icon(tag="pencil", size=18, aria_hidden="true"),
                type="button",
                aria_label=f"Editar registro de sono de {registro['data']}",
                title="Editar este registro",
                on_click=SonoState.start_edit(registro["id"]),
                class_name="sono-edit",
            ),
            rx.el.button(
                rx.icon(tag="trash-2", size=18, aria_hidden="true"),
                type="button",
                aria_label=f"Excluir registro de sono de {registro['data']}",
                title="Excluir este registro",
                on_click=SonoState.ask_delete(registro["id"]),
                class_name="ref-delete",
            ),
            class_name="ref-item-top",
        ),
        rx.el.p(registro["intervalo"], class_name="ref-description"),
        rating(registro),
        rx.cond(
            registro["observacoes"] != "",
            rx.el.p(registro["observacoes"], class_name="ref-macros"),
            rx.fragment(),
        ),
        class_name="ref-item",
    )


def empty_state() -> rx.Component:
    return rx.box(
        rx.box(rx.icon(tag="moon", size=22, aria_hidden="true"), class_name="ref-header-icon"),
        rx.el.p("Nenhum registro de sono ainda", class_name="ref-empty-title"),
        rx.el.p("Preencha o horário de início e de fim do sono para começar.", class_name="ref-empty-text"),
        class_name="ref-empty",
    )


def list_error() -> rx.Component:
    return rx.box(
        rx.el.p(SonoState.erro_lista, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            title="Busca seus registros de sono de novo",
            on_click=SonoState.start_page,
            class_name="ref-button-secondary",
        ),
        class_name="ref-error",
    )


def records_list() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Histórico", id="sono-historico-titulo", class_name="ref-list-title"),
        rx.cond(
            SonoState.carregando,
            rx.box(
                rx.box(class_name="ref-skeleton"),
                rx.box(class_name="ref-skeleton"),
                class_name="ref-list",
                aria_busy="true",
                aria_label="Carregando registros de sono",
            ),
            rx.cond(
                SonoState.erro_lista != "",
                list_error(),
                rx.cond(
                    SonoState.registros.length() == 0,
                    empty_state(),
                    rx.el.ul(rx.foreach(SonoState.registros, record_item), class_name="ref-list"),
                ),
            ),
        ),
        aria_labelledby="sono-historico-titulo",
        class_name="ref-list-section",
    )


def delete_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Excluir registro de sono?"),
            rx.alert_dialog.description(
                "Ele sai do seu histórico e das recomendações. Essa ação não pode ser desfeita."
            ),
            rx.box(
                rx.alert_dialog.cancel(
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        title="Mantém o registro",
                        class_name="ref-button-secondary",
                    ),
                ),
                rx.el.button(
                    rx.cond(SonoState.excluindo, rx.spinner(size="2"), rx.icon(tag="trash-2", size=16, aria_hidden="true")),
                    "Excluir",
                    type="button",
                    title="Exclui o registro definitivamente",
                    on_click=SonoState.confirm_delete,
                    disabled=SonoState.excluindo,
                    class_name="ref-button ref-button-danger",
                ),
                class_name="ref-alert-actions",
            ),
            class_name="ref-alert",
        ),
        open=SonoState.exclusao_id != "",
        on_open_change=SonoState.set_delete_open,
    )


def sono_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(
            page_header(),
            sleep_form(),
            records_list(),
            delete_dialog(),
            class_name="ref-page",
        ),
        REFEICOES_PAGE_CSS + SONO_PAGE_CSS,
    )
