"""Páginas provisórias das áreas privadas que ainda não foram implementadas."""

from collections.abc import Callable

import reflex as rx

from projetofacul.components.app_shell import app_shell

# rota -> (título, texto); sem dados nem formulários, só o aviso de construção
AREAS_EM_CONSTRUCAO: dict[str, tuple[str, str]] = {
    "/inicio": ("Início", "Seu resumo do dia vai aparecer aqui."),
    "/sono": ("Sono", "O registro de sono está em construção."),
    "/peso": ("Peso", "O registro de peso está em construção."),
    "/relatorios": ("Relatórios", "Os relatórios de evolução estão em construção."),
}


def build_placeholder_page(rota: str, titulo: str, descricao: str) -> Callable[[], rx.Component]:
    def placeholder_page() -> rx.Component:
        return app_shell(
            rota,
            rx.box(
                rx.heading(titulo, as_="h1", class_name="app-placeholder-title"),
                rx.text(descricao, class_name="app-placeholder-text"),
            ),
        )

    return placeholder_page
