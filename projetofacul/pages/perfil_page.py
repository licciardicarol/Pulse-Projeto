"""Tela /perfil: Dados pessoais, Biotipo corporal e Preferências de treino."""

from collections.abc import Sequence

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.logic.perfil_opcoes import (
    OPCOES_BIOTIPO,
    OPCOES_CONDICIONAMENTO,
    OPCOES_HORARIO,
    OPCOES_MODALIDADES,
    OPCOES_OBJETIVO,
    OPCOES_SEXO,
)
from projetofacul.states.perfil_state import PerfilState
from projetofacul.states.sessao_state import SessaoState
from styles.theme import apply_theme_tokens

ROTA = "/perfil"

SETA_SELECT = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' "
    "viewBox='0 0 24 24' fill='none' stroke='%239FB0C8' stroke-width='2' stroke-linecap='round' "
    "stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E\")"
)

PERFIL_PAGE_CSS = apply_theme_tokens("""
.perfil-page { max-width: 768px; }
.perfil-banner {
  display: flex; align-items: center; gap: 10px; margin: 0 0 20px; padding: 12px 14px;
  border: 1px solid __BORDER_STRONG__; border-radius: 12px; color: #CFE3FF; background: __PRIMARY_SOFT__;
  font-size: 14px; line-height: 1.5;
}
.perfil-banner p { margin: 0; }
.perfil-header { margin-bottom: 32px; }
.perfil-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.perfil-header-icon {
  width: 36px; height: 36px; flex: none; display: grid; place-items: center;
  border-radius: 50%; color: __PRIMARY__; background: #14284A;
}
.perfil-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.perfil-subtitle { margin: 0; max-width: 740px; color: __TEXT_SECONDARY__; font-size: 16px; line-height: 1.6; }
.perfil-cards { display: grid; gap: 32px; }
.perfil-card {
  min-width: 0; padding: 22px 20px 20px; border: 1px solid rgba(255,255,255,.1); border-radius: 20px;
  background: linear-gradient(180deg, #16223A 0%, __SURFACE__ 100%); box-shadow: 0 18px 45px rgba(0,0,0,.25);
  animation: perfil-rise 480ms cubic-bezier(.2,.8,.2,1) both;
}
.perfil-card:nth-child(2) { animation-delay: 70ms; }
.perfil-card:nth-child(3) { animation-delay: 140ms; }
.perfil-card-title { margin: 0 0 14px; font-size: 19px; line-height: 1.3; font-weight: 800; }
.perfil-card-text { margin: -6px 0 16px; color: __TEXT_SECONDARY__; font-size: 14.5px; line-height: 1.5; }
.perfil-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px 12px; }
.perfil-field { min-width: 0; }
.perfil-field-full { margin-top: 16px; }
.perfil-label { display: block; margin-bottom: 7px; color: #E8EEF8; font-size: 14px; font-weight: 600; }
.perfil-input {
  width: 100%; min-height: 38px; padding: 0 12px; border: 1px solid rgba(255,255,255,.1); border-radius: 10px;
  outline: none; color: __TEXT_PRIMARY__; background: rgba(255,255,255,.025); font: inherit; font-size: 14px;
  color-scheme: dark; transition: border-color 150ms ease, box-shadow 150ms ease, background 150ms ease;
}
.perfil-input:hover { border-color: rgba(255,255,255,.18); }
.perfil-input:focus { border-color: __PRIMARY__; box-shadow: 0 0 0 3px rgba(43,140,255,.2); }
.perfil-input[aria-invalid="true"] { border-color: #D6818B; }
.perfil-input[type="number"] { appearance: textfield; -moz-appearance: textfield; }
.perfil-input[type="number"]::-webkit-inner-spin-button,
.perfil-input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.perfil-input[type="date"]::-webkit-calendar-picker-indicator { opacity: .75; cursor: pointer; }
.perfil-select {
  appearance: none; -webkit-appearance: none; padding-right: 36px; cursor: pointer;
  background-image: __SETA__; background-repeat: no-repeat; background-position: right 12px center;
}
.perfil-select.is-empty { color: #8A9AB2; }
.perfil-select option { color: __TEXT_PRIMARY__; background: __SURFACE__; }
.perfil-error { margin: 6px 0 0; color: #F0A1A9; font-size: 12.5px; line-height: 1.4; }
.perfil-error:empty { margin: 0; }
.perfil-biotipos { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.perfil-biotipo {
  position: relative; min-width: 0; min-height: 124px; display: grid; align-content: center; gap: 6px;
  padding: 18px 16px; border: 1px solid rgba(255,255,255,.1); border-radius: 16px;
  background: rgba(255,255,255,.02); cursor: pointer;
  transition: border-color 150ms ease, background 150ms ease, transform 150ms ease;
}
.perfil-biotipo:hover { border-color: rgba(59,147,255,.35); background: rgba(43,140,255,.05); }
.perfil-biotipo:active { transform: scale(.99); }
.perfil-biotipo.is-selected {
  border-color: __PRIMARY__; background: linear-gradient(180deg, rgba(43,140,255,.16) 0%, rgba(43,140,255,.08) 100%);
}
.perfil-biotipo:has(.perfil-radio:focus-visible) { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
.perfil-radio { position: absolute; width: 1px; height: 1px; margin: 0; opacity: 0; pointer-events: none; }
.perfil-biotipo-title { color: __TEXT_PRIMARY__; font-size: 16px; font-weight: 700; }
.perfil-biotipo-text { color: __TEXT_SECONDARY__; font-size: 12.5px; line-height: 1.45; }
.perfil-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.perfil-chip {
  min-height: 36px; padding: 0 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 999px;
  color: __TEXT_SECONDARY__; background: transparent; font: inherit; font-size: 14px; cursor: pointer;
  transition: border-color 150ms ease, color 150ms ease, background 150ms ease, transform 150ms ease;
}
.perfil-chip:hover { border-color: rgba(59,147,255,.4); color: __TEXT_PRIMARY__; }
.perfil-chip:active { transform: scale(.97); }
.perfil-chip.is-active { border-color: __PRIMARY__; color: __TEXT_PRIMARY__; background: rgba(43,140,255,.16); }
.perfil-chip:focus-visible, .perfil-save:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }
.perfil-actions { display: grid; justify-items: end; gap: 12px; margin-top: 32px; }
.perfil-global-error {
  width: 100%; margin: 0; padding: 11px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px;
  color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px; line-height: 1.5;
}
.perfil-global-error:empty { padding: 0; border: 0; }
.perfil-save {
  min-height: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 9px; padding: 0 22px;
  border: 0; border-radius: 10px; color: __TEXT_PRIMARY__; background: __PRIMARY__;
  box-shadow: 0 10px 26px rgba(43,140,255,.18); font: inherit; font-size: 14px; font-weight: 700; cursor: pointer;
  transition: transform 170ms ease, box-shadow 170ms ease, background 170ms ease, opacity 170ms ease;
}
.perfil-save:hover:not(:disabled) { transform: translateY(-1px); background: __PRIMARY_HOVER__; box-shadow: 0 14px 30px rgba(43,140,255,.26); }
.perfil-save:active:not(:disabled) { transform: scale(.98); }
.perfil-save:disabled { opacity: .72; cursor: wait; }
@keyframes perfil-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@media (pointer: coarse) {
  .perfil-input, .perfil-chip { min-height: 44px; }
}
@media (max-width: 768px) {
  .perfil-grid, .perfil-biotipos { grid-template-columns: minmax(0, 1fr); }
  .perfil-biotipo { min-height: 0; }
  .perfil-actions { justify-items: stretch; }
  .perfil-save { width: 100%; }
  .perfil-title { font-size: 28px; }
}
@media (max-width: 520px) {
  .perfil-card { padding: 18px 16px; border-radius: 16px; }
  .perfil-subtitle { font-size: 14.5px; }
}
@media (prefers-reduced-motion: reduce) {
  .perfil-card { animation: none; }
}
""").replace("__SETA__", SETA_SELECT)


def field_error(campo: str, input_id: str) -> rx.Component:
    # sempre no DOM para o aria-live anunciar quando a mensagem aparecer
    return rx.el.p(
        PerfilState.erros.get(campo, ""),
        id=f"{input_id}-erro",
        aria_live="polite",
        class_name="perfil-error",
    )


def form_field(rotulo: str, input_id: str, controle: rx.Component, campo: str) -> rx.Component:
    return rx.box(
        rx.el.label(rotulo, html_for=input_id, class_name="perfil-label"),
        controle,
        field_error(campo, input_id),
        class_name="perfil-field",
    )


def text_input(campo: str, input_id: str, **props) -> rx.Component:
    return rx.el.input(
        id=input_id,
        name=campo,
        value=getattr(PerfilState, campo),
        on_change=lambda valor: PerfilState.update_field(campo, valor),
        aria_invalid=PerfilState.erros.contains(campo),
        aria_describedby=f"{input_id}-erro",
        class_name="perfil-input",
        **props,
    )


def select_input(campo: str, input_id: str, opcoes: Sequence[str], autocomplete: str = "off") -> rx.Component:
    valor = getattr(PerfilState, campo)
    return rx.el.select(
        rx.el.option("Selecione", value="", disabled=True),
        *[rx.el.option(opcao, value=opcao) for opcao in opcoes],
        id=input_id,
        name=campo,
        value=valor,
        on_change=lambda novo_valor: PerfilState.update_field(campo, novo_valor),
        auto_complete=autocomplete,
        aria_invalid=PerfilState.erros.contains(campo),
        aria_describedby=f"{input_id}-erro",
        class_name=rx.cond(valor == "", "perfil-input perfil-select is-empty", "perfil-input perfil-select"),
    )


def profile_card(titulo: str, titulo_id: str, *conteudo: rx.Component) -> rx.Component:
    return rx.el.section(
        rx.el.h2(titulo, id=titulo_id, class_name="perfil-card-title"),
        *conteudo,
        aria_labelledby=titulo_id,
        class_name="perfil-card",
    )


def dados_pessoais_card() -> rx.Component:
    return profile_card(
        "Dados pessoais",
        "perfil-dados-titulo",
        rx.box(
            form_field(
                "Nome completo",
                "perfil-nome",
                text_input("nome", "perfil-nome", type="text", auto_complete="name", max_length=50),
                "nome",
            ),
            form_field(
                "Data de nascimento",
                "perfil-nascimento",
                text_input("data_de_nascimento", "perfil-nascimento", type="date", auto_complete="bday", min="1900-01-01"),
                "data_de_nascimento",
            ),
            form_field("Sexo", "perfil-sexo", select_input("sexo", "perfil-sexo", OPCOES_SEXO, "sex"), "sexo"),
            form_field(
                "Altura (cm)",
                "perfil-altura",
                text_input(
                    "altura_cm",
                    "perfil-altura",
                    type="number",
                    input_mode="decimal",
                    auto_complete="off",
                    min="100",
                    max="250",
                    step="any",
                ),
                "altura_cm",
            ),
            class_name="perfil-grid",
        ),
    )


def biotipo_option(valor: str, descricao: str) -> rx.Component:
    selecionado = PerfilState.tipo_fisico == valor
    return rx.el.label(
        rx.el.input(
            type="radio",
            name="tipo_fisico",
            value=valor,
            checked=selecionado,
            on_change=lambda novo_valor: PerfilState.update_field("tipo_fisico", novo_valor),
            class_name="perfil-radio",
        ),
        rx.el.span(valor, class_name="perfil-biotipo-title"),
        rx.el.span(descricao, class_name="perfil-biotipo-text"),
        class_name=rx.cond(selecionado, "perfil-biotipo is-selected", "perfil-biotipo"),
    )


def biotipo_card() -> rx.Component:
    return profile_card(
        "Biotipo corporal",
        "perfil-biotipo-titulo",
        rx.el.p(
            "Selecione o que mais se parece com você. Isso ajuda a calibrar recomendações.",
            id="perfil-biotipo-descricao",
            class_name="perfil-card-text",
        ),
        rx.box(
            *[biotipo_option(valor, descricao) for valor, descricao in OPCOES_BIOTIPO],
            role="radiogroup",
            aria_labelledby="perfil-biotipo-titulo",
            aria_describedby="perfil-biotipo-descricao perfil-biotipo-erro",
            class_name="perfil-biotipos",
        ),
        field_error("tipo_fisico", "perfil-biotipo"),
    )


def modalidade_chip(modalidade: str) -> rx.Component:
    ativa = PerfilState.modalidade_fav1.contains(modalidade)
    return rx.el.button(
        modalidade,
        type="button",
        aria_pressed=ativa,
        on_click=PerfilState.toggle_modalidade(modalidade),
        class_name=rx.cond(ativa, "perfil-chip is-active", "perfil-chip"),
    )


def preferencias_treino_card() -> rx.Component:
    return profile_card(
        "Preferências de treino",
        "perfil-treino-titulo",
        rx.box(
            form_field(
                "Condicionamento",
                "perfil-condicionamento",
                select_input("nivel_fisico", "perfil-condicionamento", OPCOES_CONDICIONAMENTO),
                "nivel_fisico",
            ),
            form_field(
                "Horário habitual",
                "perfil-horario",
                select_input("horario_fav_de_treino", "perfil-horario", OPCOES_HORARIO),
                "horario_fav_de_treino",
            ),
            form_field(
                "Meta semanal (treinos)",
                "perfil-meta",
                text_input(
                    "meta_semanal",
                    "perfil-meta",
                    type="number",
                    input_mode="numeric",
                    auto_complete="off",
                    min="1",
                    max="14",
                    step="1",
                ),
                "meta_semanal",
            ),
            form_field(
                "Objetivo",
                "perfil-objetivo",
                select_input("objetivo", "perfil-objetivo", OPCOES_OBJETIVO),
                "objetivo",
            ),
            class_name="perfil-grid",
        ),
        rx.box(
            rx.el.span("Modalidades favoritas", id="perfil-modalidades-rotulo", class_name="perfil-label"),
            rx.box(
                *[modalidade_chip(modalidade) for modalidade in OPCOES_MODALIDADES],
                role="group",
                aria_labelledby="perfil-modalidades-rotulo",
                aria_describedby="perfil-modalidades-erro",
                class_name="perfil-chips",
            ),
            field_error("modalidade_fav1", "perfil-modalidades"),
            class_name="perfil-field perfil-field-full",
        ),
    )


def onboarding_banner() -> rx.Component:
    return rx.cond(
        SessaoState.onboarding_concluido,
        rx.fragment(),
        rx.box(
            rx.icon(tag="info", size=18, aria_hidden="true"),
            rx.el.p("Complete seu perfil para personalizar suas recomendações"),
            role="status",
            class_name="perfil-banner",
        ),
    )


def perfil_header() -> rx.Component:
    return rx.box(
        rx.box(
            rx.box(rx.icon(tag="user", size=18, aria_hidden="true"), class_name="perfil-header-icon"),
            rx.el.h1("Perfil", class_name="perfil-title"),
            class_name="perfil-header-row",
        ),
        rx.el.p(
            "Suas informações pessoais e preferências de treino, usadas para personalizar "
            "as recomendações e o cálculo de calorias.",
            class_name="perfil-subtitle",
        ),
        class_name="perfil-header",
    )


def save_actions() -> rx.Component:
    return rx.box(
        rx.el.p(PerfilState.erro_geral, aria_live="polite", class_name="perfil-global-error"),
        rx.el.button(
            rx.cond(
                PerfilState.salvando,
                rx.spinner(size="2"),
                rx.icon(tag="save", size=18, aria_hidden="true"),
            ),
            "Salvar perfil",
            type="button",
            on_click=PerfilState.save_profile,
            disabled=PerfilState.salvando,
            aria_busy=PerfilState.salvando,
            class_name="perfil-save",
        ),
        class_name="perfil-actions",
    )


def perfil_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(
            onboarding_banner(),
            perfil_header(),
            rx.box(
                dados_pessoais_card(),
                biotipo_card(),
                preferencias_treino_card(),
                class_name="perfil-cards",
            ),
            save_actions(),
            class_name="perfil-page",
        ),
        PERFIL_PAGE_CSS,
    )
