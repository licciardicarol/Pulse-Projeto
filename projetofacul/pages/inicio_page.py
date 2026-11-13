"""Tela /inicio: card "Recomendação de hoje" gerado por IA a partir dos registros do usuário."""

import reflex as rx

from projetofacul.components.app_shell import app_shell
from projetofacul.states.inicio_state import InicioState
from styles.theme import apply_theme_tokens

ROTA = "/inicio"

SUBTITULO = "Sua recomendação de treino para hoje, a partir dos seus registros."
AVISO_IA = (
    "Recomendação gerada por IA a partir dos seus registros. "
    "Não substitui a orientação de um profissional de saúde ou de educação física."
)
TITULO_SEM_DADOS = "Comece registrando sua rotina"
TEXTO_SEM_DADOS = (
    "Registre seu sono, suas refeições ou um treino para receber uma recomendação de treino "
    "feita a partir dos seus dados."
)
TEXTO_PREPARANDO = "Preparando sua recomendação…"

# (ícone, texto, rota) dos atalhos do estado sem registros
ATALHOS_REGISTRO = (
    ("moon", "Registrar sono", "/sono"),
    ("utensils", "Registrar refeição", "/refeicoes"),
    ("dumbbell", "Registrar treino", "/treinos"),
)

INICIO_PAGE_CSS = apply_theme_tokens("""
.ini-page { width: min(1200px, 100%); margin: 0 auto; }
.ini-header { margin-bottom: 24px; }
.ini-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.ini-header-icon {
  width: 40px; height: 40px; flex: none; display: grid; place-items: center; border-radius: 50%;
  color: __PRIMARY__; background: rgba(43,140,255,.14);
}
.ini-title { margin: 0; font-size: 32px; line-height: 1.1; font-weight: 800; }
.ini-subtitle { margin: 0; max-width: 640px; color: __TEXT_SECONDARY__; font-size: 15.5px; line-height: 1.6; }

.ini-card {
  padding: 24px; border: 1px solid __BORDER__; border-radius: 18px; background: __SURFACE__;
  animation: ini-fade-in 260ms ease both;
}
.ini-card-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.ini-card-title {
  display: inline-flex; align-items: center; gap: 8px; margin: 0; color: __TEXT_SECONDARY__;
  font-size: 12.5px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase;
}
.ini-card-title svg { color: __PRIMARY__; }
.ini-card-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ini-generated { color: __TEXT_MUTED__; font-size: 12.5px; }
.ini-refresh {
  min-height: 44px; display: inline-flex; align-items: center; gap: 7px; padding: 0 14px;
  border: 1px solid rgba(43,140,255,.45); border-radius: 10px; color: #BFDAFF; background: rgba(43,140,255,.10);
  font: inherit; font-size: 13.5px; font-weight: 700; cursor: pointer; transition: background 160ms ease, transform 160ms ease;
}
.ini-refresh:hover:not(:disabled) { background: rgba(43,140,255,.2); }
.ini-refresh:active:not(:disabled) { transform: scale(.98); }
.ini-refresh:disabled { opacity: .72; cursor: wait; }
.ini-refresh:focus-visible, .ini-retry:focus-visible, .ini-shortcut:focus-visible { outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px; }

.ini-headline { margin: 0 0 6px; font-size: 19px; line-height: 1.35; font-weight: 800; overflow-wrap: anywhere; }
.ini-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; line-height: 1.6; overflow-wrap: anywhere; }
.ini-boxes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
.ini-box {
  min-width: 0; padding: 16px 18px; border: 1px solid __BORDER__; border-radius: 14px; background: rgba(255,255,255,.02);
  transition: border-color 170ms ease;
}
.ini-box:hover { border-color: rgba(59,147,255,.35); }
.ini-box-label {
  display: flex; align-items: center; gap: 6px; margin: 0 0 8px; color: __TEXT_SECONDARY__;
  font-size: 11.5px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
}
.ini-recovery { margin: 0; font-size: 28px; line-height: 1.1; font-weight: 800; }
.ini-recovery-max { margin-left: 2px; color: __TEXT_SECONDARY__; font-size: 15px; font-weight: 700; }
.ini-intensity { margin: 0 0 6px; font-size: 22px; line-height: 1.2; font-weight: 800; }
.ini-box-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 13.5px; line-height: 1.5; overflow-wrap: anywhere; }
.ini-food { margin: 0; color: __TEXT_PRIMARY__; font-size: 14px; line-height: 1.55; overflow-wrap: anywhere; }
.ini-ai-note { display: flex; align-items: flex-start; gap: 8px; margin: 16px 0 0; color: __TEXT_SECONDARY__; font-size: 13px; line-height: 1.5; }
.ini-ai-note svg { flex: none; margin-top: 2px; color: __PRIMARY__; }
.ini-inline-error { margin: 0 0 12px; padding: 10px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px; color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px; }
.ini-inline-error:empty { display: none; }
.ini-sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }

.ini-preparing { display: grid; gap: 12px; }
.ini-preparing-text { display: inline-flex; align-items: center; gap: 8px; margin: 0; color: #BFDAFF; font-size: 14px; font-weight: 600; }
.ini-skeleton { border-radius: 10px; background: linear-gradient(90deg, rgba(255,255,255,.04), rgba(255,255,255,.09), rgba(255,255,255,.04)); background-size: 200% 100%; animation: ini-shimmer 1.2s ease-in-out infinite; }
.ini-skeleton-line { height: 18px; }
.ini-skeleton-line.ini-short { width: 60%; }
.ini-skeleton-box { height: 96px; }
.ini-spinner {
  width: 14px; height: 14px; flex: none; border-radius: 50%; border: 2px solid rgba(191,218,255,.35); border-top-color: #BFDAFF;
  animation: ini-spin 800ms linear infinite;
}

.ini-empty { display: grid; gap: 10px; }
.ini-empty-title { margin: 0; font-size: 18px; font-weight: 800; }
.ini-empty-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 14.5px; line-height: 1.6; }
.ini-shortcuts { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; }
.ini-shortcut {
  min-height: 44px; display: inline-flex; align-items: center; gap: 8px; padding: 0 16px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__ !important;
  font-size: 14px; font-weight: 600; text-decoration: none !important; transition: background 160ms ease, border-color 160ms ease;
}
.ini-shortcut:hover { background: rgba(255,255,255,.06); border-color: rgba(59,147,255,.35); }
.ini-shortcut svg { color: __PRIMARY__; }

.ini-error { display: grid; justify-items: start; gap: 12px; }
.ini-error p { margin: 0; color: #F2B1B7; font-size: 14.5px; }
.ini-retry {
  min-height: 44px; display: inline-flex; align-items: center; gap: 8px; padding: 0 18px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 160ms ease;
}
.ini-retry:hover { background: rgba(255,255,255,.06); }

@keyframes ini-fade-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes ini-shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
@keyframes ini-spin { to { transform: rotate(360deg); } }

@media (max-width: 720px) {
  .ini-boxes { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 640px) {
  .ini-title { font-size: 27px; }
  .ini-card { padding: 18px 16px; }
  .ini-card-actions { width: 100%; justify-content: space-between; }
  .ini-shortcut { flex: 1 1 100%; justify-content: center; }
}
@media (prefers-reduced-motion: reduce) {
  .ini-card, .ini-skeleton, .ini-spinner { animation: none !important; }
  .ini-refresh:active:not(:disabled) { transform: none; }
}
""")


def page_header() -> rx.Component:
    return rx.el.header(
        rx.box(
            rx.box(rx.icon(tag="house", size=20, aria_hidden="true"), class_name="ini-header-icon"),
            rx.el.h1("Início", class_name="ini-title"),
            class_name="ini-header-row",
        ),
        rx.el.p(SUBTITULO, class_name="ini-subtitle"),
        class_name="ini-header",
    )


def refresh_button() -> rx.Component:
    return rx.el.button(
        rx.cond(
            InicioState.atualizando,
            rx.fragment(rx.box(class_name="ini-spinner", aria_hidden="true"), "Atualizando…"),
            rx.fragment(rx.icon(tag="refresh-cw", size=16, aria_hidden="true"), "Atualizar"),
        ),
        type="button",
        aria_label="Atualizar recomendação de hoje",
        title="Gera uma nova recomendação com os seus registros atuais",
        disabled=InicioState.atualizando,
        on_click=InicioState.refresh_recommendation,
        class_name="ini-refresh",
    )


def card_top() -> rx.Component:
    return rx.box(
        rx.el.h2(
            rx.icon(tag="sparkles", size=16, aria_hidden="true"),
            "Recomendação de hoje",
            id="ini-card-titulo",
            class_name="ini-card-title",
        ),
        rx.cond(
            InicioState.estado == "pronta",
            rx.box(
                rx.el.span(InicioState.recomendacao["gerada_em"], class_name="ini-generated"),
                refresh_button(),
                class_name="ini-card-actions",
            ),
            rx.fragment(),
        ),
        class_name="ini-card-top",
    )


def recovery_box() -> rx.Component:
    return rx.box(
        rx.el.p(rx.icon(tag="activity", size=14, aria_hidden="true"), "Recuperação", class_name="ini-box-label"),
        rx.el.p(
            rx.el.span(
                InicioState.recomendacao["recuperacao"],
                rx.el.span("/100", class_name="ini-recovery-max"),
                aria_hidden="true",
            ),
            rx.el.span(InicioState.recomendacao["recuperacao_rotulo"], class_name="ini-sr-only"),
            class_name="ini-recovery",
        ),
        class_name="ini-box",
    )


def training_box() -> rx.Component:
    return rx.box(
        rx.el.p(rx.icon(tag="dumbbell", size=14, aria_hidden="true"), "Treino sugerido", class_name="ini-box-label"),
        # a intensidade é comunicada por texto, não por cor
        rx.el.p(InicioState.recomendacao["intensidade"], class_name="ini-intensity"),
        rx.el.p(InicioState.recomendacao["motivo_treino"], class_name="ini-box-text"),
        class_name="ini-box",
    )


def food_box() -> rx.Component:
    return rx.box(
        rx.el.p(rx.icon(tag="utensils", size=14, aria_hidden="true"), "Alimentação", class_name="ini-box-label"),
        rx.el.p(InicioState.recomendacao["alimentacao"], class_name="ini-food"),
        class_name="ini-box",
    )


def ready_content() -> rx.Component:
    return rx.box(
        # falha do "Atualizar": a recomendação anterior continua logo abaixo
        rx.el.p(InicioState.mensagem_erro, aria_live="polite", class_name="ini-inline-error"),
        # texto puro: o Reflex escapa o conteúdo vindo da IA
        rx.el.h3(InicioState.recomendacao["titulo"], class_name="ini-headline"),
        rx.el.p(InicioState.recomendacao["texto"], class_name="ini-text"),
        rx.box(recovery_box(), training_box(), food_box(), class_name="ini-boxes"),
        # aviso fixo: sempre junto da recomendação
        rx.el.p(rx.icon(tag="info", size=15, aria_hidden="true"), AVISO_IA, class_name="ini-ai-note"),
    )


def preparing_content() -> rx.Component:
    return rx.box(
        rx.el.p(
            rx.box(class_name="ini-spinner", aria_hidden="true"),
            TEXTO_PREPARANDO,
            role="status",
            class_name="ini-preparing-text",
        ),
        rx.box(class_name="ini-skeleton ini-skeleton-line", aria_hidden="true"),
        rx.box(class_name="ini-skeleton ini-skeleton-line ini-short", aria_hidden="true"),
        rx.box(
            rx.box(class_name="ini-skeleton ini-skeleton-box"),
            rx.box(class_name="ini-skeleton ini-skeleton-box"),
            rx.box(class_name="ini-skeleton ini-skeleton-box"),
            class_name="ini-boxes",
            aria_hidden="true",
        ),
        aria_busy="true",
        class_name="ini-preparing",
    )


def empty_content() -> rx.Component:
    return rx.box(
        rx.el.p(TITULO_SEM_DADOS, class_name="ini-empty-title"),
        rx.el.p(TEXTO_SEM_DADOS, class_name="ini-empty-text"),
        rx.box(
            *[
                rx.link(rx.icon(tag=icone, size=16, aria_hidden="true"), texto, href=rota, class_name="ini-shortcut")
                for icone, texto, rota in ATALHOS_REGISTRO
            ],
            class_name="ini-shortcuts",
        ),
        class_name="ini-empty",
    )


def error_content() -> rx.Component:
    return rx.box(
        rx.el.p(InicioState.mensagem_erro, role="status", aria_live="polite"),
        rx.el.button(
            rx.icon(tag="rotate-cw", size=16, aria_hidden="true"),
            "Tentar novamente",
            type="button",
            title="Busca a recomendação de hoje de novo",
            on_click=InicioState.start_page,
            class_name="ini-retry",
        ),
        class_name="ini-error",
    )


def recommendation_card() -> rx.Component:
    return rx.el.section(
        card_top(),
        rx.match(
            InicioState.estado,
            ("pronta", ready_content()),
            ("sem_dados", empty_content()),
            ("erro", error_content()),
            preparing_content(),
        ),
        aria_labelledby="ini-card-titulo",
        class_name="ini-card",
    )


def inicio_page() -> rx.Component:
    return app_shell(
        ROTA,
        rx.box(page_header(), recommendation_card(), class_name="ini-page"),
        INICIO_PAGE_CSS,
    )
