"""Estrutura comum das páginas logadas: fontes, CSS, navbar e guarda de sessão."""

import reflex as rx

from projetofacul.components.navbar import navbar
from projetofacul.states.sessao_state import SessaoState
from styles.theme import apply_theme_tokens

APP_SHELL_CSS = apply_theme_tokens("""
html, body, #root { min-height: 100%; margin: 0; }
body { background: __BACKGROUND__; }
.app-page {
  min-height: 100vh; color: __TEXT_PRIMARY__; background: __BACKGROUND__;
  font-family: __FONT__; overflow-x: hidden;
}
.app-page *, .app-page *::before, .app-page *::after { box-sizing: border-box; }
.app-nav {
  position: sticky; top: 0; z-index: 30; background: rgba(11,18,32,.92);
  backdrop-filter: blur(14px); border-bottom: 1px solid rgba(255,255,255,.07);
}
.app-nav-inner {
  width: min(1160px, 100%); min-height: 56px; margin: 0 auto; padding: 0 24px;
  display: flex; align-items: center; gap: 20px;
}
.app-nav-brand { display: inline-flex; align-items: center; gap: 10px; color: __TEXT_PRIMARY__; text-decoration: none; }
.app-nav-mark {
  width: 32px; height: 32px; display: grid; place-items: center; border-radius: 50%;
  color: __PRIMARY__; background: #14284A;
}
.app-nav-name { font-size: 17px; font-weight: 800; }
.app-nav-links { display: flex; align-items: center; gap: 2px; margin: 0 auto; }
.app-nav-link {
  display: inline-flex; align-items: center; gap: 8px; min-height: 36px; padding: 0 12px;
  border-radius: 999px; color: __TEXT_SECONDARY__; font-size: 14.5px; font-weight: 500;
  text-decoration: none; white-space: nowrap; transition: color 150ms ease, background 150ms ease;
}
.app-nav-link:hover { color: __TEXT_PRIMARY__; background: rgba(255,255,255,.04); }
.app-nav-link[aria-current="page"] { color: __PRIMARY_HOVER__; background: rgba(43,140,255,.16); }
.app-nav-logout {
  display: inline-flex; align-items: center; gap: 8px; min-height: 36px; padding: 0 10px;
  border: 0; border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent;
  font: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
}
.app-nav-logout:hover { background: rgba(255,255,255,.06); }
.app-nav-menu-button {
  display: none; width: 44px; height: 44px; margin-left: auto; place-items: center;
  border: 0; border-radius: 10px; color: __TEXT_PRIMARY__; background: transparent; cursor: pointer;
}
.app-nav-panel { display: none; }
.app-nav-link:focus-visible, .app-nav-logout:focus-visible, .app-nav-menu-button:focus-visible, .app-nav-brand:focus-visible {
  outline: 3px solid rgba(43,140,255,.65); outline-offset: 2px;
}
.app-main { width: min(1160px, 100%); margin: 0 auto; padding: 28px 24px 64px; }
.app-status { display: grid; place-items: center; min-height: 40vh; color: __TEXT_SECONDARY__; }
.app-placeholder-title { margin: 0 0 8px; font-size: 32px; font-weight: 800; }
.app-placeholder-text { margin: 0; color: __TEXT_SECONDARY__; font-size: 16px; }
@media (pointer: coarse) {
  .app-nav-link, .app-nav-logout { min-height: 44px; }
}
@media (max-width: 980px) {
  .app-nav-links, .app-nav-actions { display: none; }
  .app-nav-menu-button { display: grid; }
  .app-nav-panel.is-open {
    display: grid; gap: 4px; padding: 8px 16px 16px; border-top: 1px solid rgba(255,255,255,.06);
  }
  .app-nav-panel .app-nav-link, .app-nav-panel .app-nav-logout {
    min-height: 44px; width: 100%; justify-content: flex-start; padding: 0 14px; border-radius: 12px;
  }
}
@media (max-width: 520px) {
  .app-nav-inner { padding: 0 16px; }
  .app-main { padding: 20px 16px 48px; }
}
@media (prefers-reduced-motion: reduce) {
  .app-page *, .app-page *::before, .app-page *::after {
    transition-duration: .01ms !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
  }
}
""")

FONTES_HTML = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'
    '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />'
)


def session_guard(conteudo: rx.Component) -> rx.Component:
    """Só exibe o conteúdo privado depois que a sessão foi confirmada no Xano."""
    return rx.cond(
        SessaoState.sessao_verificada,
        conteudo,
        rx.box(
            rx.cond(
                SessaoState.erro_sessao != "",
                rx.text(SessaoState.erro_sessao, role="status", aria_live="polite"),
                rx.spinner(size="3", aria_label="Carregando"),
            ),
            class_name="app-status",
        ),
    )


def app_shell(rota_ativa: str, conteudo: rx.Component, css_extra: str = "") -> rx.Component:
    return rx.box(
        rx.html(f"{FONTES_HTML}<style>{APP_SHELL_CSS}{css_extra}</style>"),
        navbar(rota_ativa),
        rx.el.main(session_guard(conteudo), class_name="app-main"),
        class_name="app-page",
    )
