"""Registro das rotas do Pulse."""

import reflex as rx

from projetofacul.auth_page import AuthState, pagina_autenticacao
from projetofacul.landing_page import landing_page
from projetofacul.pages.perfil_page import perfil_page
from projetofacul.pages.placeholder_page import AREAS_EM_CONSTRUCAO, build_placeholder_page
from projetofacul.states.perfil_state import PerfilState
from projetofacul.states.sessao_state import SessaoState


def home() -> rx.Component:
    """Retorna a landing page pública do Pulse."""
    return landing_page()


def redirect_page() -> rx.Component:
    """Página vazia usada por rotas antigas que apenas redirecionam."""
    return rx.box()


app = rx.App()
app.add_page(home, route="/")
app.add_page(
    pagina_autenticacao,
    route="/login",
    on_load=[AuthState.inicializar_login, SessaoState.redirect_if_authenticated],
)
app.add_page(
    pagina_autenticacao,
    route="/cadastro",
    on_load=[AuthState.inicializar_cadastro, SessaoState.redirect_if_authenticated],
)

# o onboarding agora acontece em /perfil
app.add_page(redirect_page, route="/onboarding", on_load=SessaoState.redirect_to_perfil)

# o guarda roda antes e já deixa o Perfil carregado no SessaoState
app.add_page(
    perfil_page,
    route="/perfil",
    title="Perfil | Pulse",
    on_load=[SessaoState.ensure_session, PerfilState.load_profile],
)

for rota, (titulo, descricao) in AREAS_EM_CONSTRUCAO.items():
    app.add_page(
        build_placeholder_page(rota, titulo, descricao),
        route=rota,
        title=f"{titulo} | Pulse",
        on_load=SessaoState.ensure_session,
    )
