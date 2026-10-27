"""Registro das rotas do Pulse."""

import reflex as rx

from projetofacul.auth_page import AuthState, pagina_autenticacao
from projetofacul.landing_page import landing_page
from projetofacul.pages.perfil_page import perfil_page
from projetofacul.pages.peso_page import peso_page
from projetofacul.pages.refeicoes_page import refeicoes_page
from projetofacul.pages.treinos_page import treinos_page
from projetofacul.pages.placeholder_page import AREAS_EM_CONSTRUCAO, build_placeholder_page
from projetofacul.pages.sono_page import sono_page
from projetofacul.states.perfil_state import PerfilState
from projetofacul.states.peso_state import PesoState
from projetofacul.states.refeicoes_state import RefeicoesState
from projetofacul.states.sessao_state import SessaoState
from projetofacul.states.treinos_state import TreinosState
from projetofacul.states.sono_state import SonoState


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

app.add_page(
    refeicoes_page,
    route="/refeicoes",
    title="Refeições | Pulse",
    on_load=[SessaoState.ensure_session, RefeicoesState.start_page],
)

app.add_page(
    treinos_page,
    route="/treinos",
    title="Treinos | Pulse",
    on_load=[SessaoState.ensure_session, TreinosState.start_page],
)

app.add_page(
    peso_page,
    route="/peso",
    title="Peso | Pulse",
    on_load=[SessaoState.ensure_session, PesoState.start_page],
)

app.add_page(
    sono_page,
    route="/sono",
    title="Sono | Pulse",
    on_load=[SessaoState.ensure_session, SonoState.start_page],
)

for rota, (titulo, descricao) in AREAS_EM_CONSTRUCAO.items():
    app.add_page(
        build_placeholder_page(rota, titulo, descricao),
        route=rota,
        title=f"{titulo} | Pulse",
        on_load=SessaoState.ensure_session,
    )
