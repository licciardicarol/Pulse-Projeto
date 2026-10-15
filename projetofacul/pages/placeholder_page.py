"""Páginas provisórias das áreas privadas que ainda não foram implementadas."""

from collections.abc import Callable

import reflex as rx

from projetofacul.states.sessao_state import SessaoState
from styles.theme import THEME

# rota -> (título, texto); sem dados nem formulários, só o aviso de construção
AREAS_EM_CONSTRUCAO: dict[str, tuple[str, str]] = {
    "/inicio": ("Início", "Seu resumo do dia vai aparecer aqui."),
    "/treinos": ("Treinos", "O registro de treinos está em construção."),
    "/refeicoes": ("Refeições", "O registro de refeições está em construção."),
    "/sono": ("Sono", "O registro de sono está em construção."),
    "/peso": ("Peso", "O registro de peso está em construção."),
    "/relatorios": ("Relatórios", "Os relatórios de evolução estão em construção."),
    "/perfil": ("Perfil", "A tela de perfil está em construção."),
}


def session_guard(conteudo: rx.Component) -> rx.Component:
    """Só exibe o conteúdo privado depois que a sessão foi confirmada no Xano."""
    return rx.cond(
        SessaoState.sessao_verificada,
        conteudo,
        rx.cond(
            SessaoState.erro_sessao != "",
            rx.text(SessaoState.erro_sessao, role="status", aria_live="polite"),
            rx.spinner(size="3", aria_label="Carregando"),
        ),
    )


def build_placeholder_page(titulo: str, descricao: str) -> Callable[[], rx.Component]:
    def placeholder_page() -> rx.Component:
        return rx.box(
            session_guard(
                rx.vstack(
                    rx.heading(titulo, as_="h1", size="7"),
                    rx.text(descricao, color=THEME.COLORS["text_secondary"]),
                    rx.button(
                        rx.icon(tag="log-out", size=16),
                        "Sair",
                        on_click=SessaoState.logout,
                        variant="outline",
                        min_height="44px",
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                    max_width="960px",
                    margin="0 auto",
                ),
            ),
            min_height="100vh",
            padding="48px 16px",
            color=THEME.COLORS["text_primary"],
            background=THEME.COLORS["background"],
            font_family=THEME.FONT_FAMILIES,
        )

    return placeholder_page
