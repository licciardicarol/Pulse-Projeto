"""Sessão do usuário autenticado no Xano."""

import reflex as rx

from projetofacul.logic.navegacao import ROTA_PERFIL, get_home_route, resolve_redirect
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError

# mesma expiração do token emitido pelo Xano (expiration = 86400)
DURACAO_SESSAO_SEGUNDOS = 86400


class SessaoState(rx.State):
    """Guarda o token e os dados mínimos do usuário logado."""

    token: str = rx.Cookie(
        "",
        name="pulse_token",
        max_age=DURACAO_SESSAO_SEGUNDOS,
        same_site="strict",
    )
    usuario_nome: str = ""
    usuario_email: str = ""
    onboarding_concluido: bool = False
    sessao_verificada: bool = False
    erro_sessao: str = ""

    @rx.var
    def autenticado(self) -> bool:
        return self.token != ""

    def clear_session(self):
        self.token = ""
        self.usuario_nome = ""
        self.usuario_email = ""
        self.onboarding_concluido = False
        self.sessao_verificada = False

    async def load_session(self) -> bool:
        """Confirma o token no Xano e carrega usuário e status do onboarding."""
        if not self.token:
            return False
        try:
            usuario = await xano_client.get_me(self.token)
            perfil = await xano_client.get_perfil(self.token)
        except XanoError as erro:
            if erro.tipo in ("nao_autorizado", "nao_encontrado"):
                self.clear_session()
                return False
            raise
        self.usuario_nome = usuario.get("nome") or ""
        self.usuario_email = usuario.get("email") or ""
        self.onboarding_concluido = bool(perfil.get("onboarding_concluido"))
        self.erro_sessao = ""
        return True

    async def start_session(self, token: str) -> str:
        """Salva o token recebido no login/cadastro e devolve a rota de destino."""
        self.token = token
        try:
            await self.load_session()
        except XanoError:
            # a conta existe e o token é válido; o guarda da rota tentará de novo
            return ROTA_PERFIL
        return get_home_route(self.onboarding_concluido)

    @rx.event
    async def ensure_session(self):
        """on_load das rotas privadas: exige sessão e onboarding concluído."""
        self.sessao_verificada = False
        try:
            autenticado = await self.load_session()
        except XanoError:
            self.erro_sessao = "Não foi possível carregar seus dados agora. Tente novamente em instantes."
            return
        destino = resolve_redirect(autenticado, self.onboarding_concluido, self.router.url.path)
        if destino:
            return rx.redirect(destino)
        self.sessao_verificada = True

    @rx.event
    async def redirect_if_authenticated(self):
        """on_load de /login e /cadastro: quem já está logado segue para o app."""
        try:
            autenticado = await self.load_session()
        except XanoError:
            return
        destino = resolve_redirect(autenticado, self.onboarding_concluido, self.router.url.path)
        if destino:
            return rx.redirect(destino)

    @rx.event
    def logout(self):
        self.clear_session()
        return rx.redirect("/")

    @rx.event
    def redirect_to_perfil(self):
        return rx.redirect(ROTA_PERFIL)
