"""Navbar da área logada (desktop + menu compacto no celular)."""

import reflex as rx

from projetofacul.states.sessao_state import SessaoState

# (rota, rótulo, ícone Lucide), na ordem exibida; sem "Social" por decisão de produto
ITENS_NAVBAR = (
    ("/inicio", "Início", "activity"),
    ("/treinos", "Treinos", "dumbbell"),
    ("/refeicoes", "Refeições", "utensils"),
    ("/sono", "Sono", "moon"),
    ("/peso", "Peso", "scale"),
    ("/relatorios", "Relatórios", "chart-line"),
    ("/perfil", "Perfil", "user"),
)


class NavbarState(rx.State):
    """Abre e fecha o menu compacto do celular."""

    menu_aberto: bool = False

    @rx.event
    def toggle_menu(self):
        self.menu_aberto = not self.menu_aberto

    @rx.event
    def close_menu(self):
        self.menu_aberto = False


def nav_link(rota: str, rotulo: str, icone: str, rota_ativa: str) -> rx.Component:
    atributos = {"aria_current": "page"} if rota == rota_ativa else {}
    return rx.link(
        rx.icon(tag=icone, size=17, aria_hidden="true"),
        rotulo,
        href=rota,
        underline="none",
        on_click=NavbarState.close_menu,
        class_name="app-nav-link",
        **atributos,
    )


def logout_button() -> rx.Component:
    return rx.el.button(
        rx.icon(tag="log-out", size=17, aria_hidden="true"),
        "Sair",
        type="button",
        on_click=[NavbarState.close_menu, SessaoState.logout],
        class_name="app-nav-logout",
    )


def navbar(rota_ativa: str) -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.link(
                rx.box(rx.icon(tag="activity", size=18, aria_hidden="true"), class_name="app-nav-mark"),
                rx.text("Pulse", as_="span", class_name="app-nav-name"),
                href="/inicio",
                underline="none",
                aria_label="Pulse, ir para o Início",
                class_name="app-nav-brand",
            ),
            rx.el.nav(
                *[nav_link(rota, rotulo, icone, rota_ativa) for rota, rotulo, icone in ITENS_NAVBAR],
                aria_label="Principal",
                class_name="app-nav-links",
            ),
            rx.box(logout_button(), class_name="app-nav-actions"),
            rx.el.button(
                rx.cond(
                    NavbarState.menu_aberto,
                    rx.icon(tag="x", size=22, aria_hidden="true"),
                    rx.icon(tag="menu", size=22, aria_hidden="true"),
                ),
                type="button",
                aria_label=rx.cond(NavbarState.menu_aberto, "Fechar menu", "Abrir menu"),
                aria_expanded=NavbarState.menu_aberto,
                aria_controls="app-nav-panel",
                on_click=NavbarState.toggle_menu,
                class_name="app-nav-menu-button",
            ),
            class_name="app-nav-inner",
        ),
        rx.el.nav(
            *[nav_link(rota, rotulo, icone, rota_ativa) for rota, rotulo, icone in ITENS_NAVBAR],
            logout_button(),
            id="app-nav-panel",
            aria_label="Menu",
            class_name=rx.cond(NavbarState.menu_aberto, "app-nav-panel is-open", "app-nav-panel"),
        ),
        class_name="app-nav",
    )
