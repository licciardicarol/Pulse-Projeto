"""Sessão do usuário autenticado no Xano."""

import time

import reflex as rx

from projetofacul.logic.navegacao import ROTA_PERFIL, get_home_route, resolve_redirect
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError

# mesma expiração do token emitido pelo Xano (expiration = 86400)
DURACAO_SESSAO_SEGUNDOS = 86400

# confirmação da sessão reaproveitada entre páginas (limite do Xano: 10 requisições / 20 s)
VALIDADE_CONFIRMACAO_SEGUNDOS = 60

MENSAGEM_FALHA_SESSAO = "Não foi possível carregar seus dados agora. Tente novamente em instantes."


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
    # último Perfil lido do Xano; só no servidor, reaproveitado pela tela de Perfil
    _perfil: dict = {}
    # último token confirmado no Xano e quando (relógio monotônico do servidor)
    _token_verificado: str = ""
    _verificada_em: float = 0.0

    @rx.var
    def autenticado(self) -> bool:
        return self.token != ""

    def clear_session(self):
        self.token = ""
        self.usuario_nome = ""
        self.usuario_email = ""
        self.onboarding_concluido = False
        self.sessao_verificada = False
        self._perfil = {}
        self._token_verificado = ""
        self._verificada_em = 0.0

    def is_confirmation_recent(self) -> bool:
        return (
            self._token_verificado == self.token
            and time.monotonic() - self._verificada_em < VALIDADE_CONFIRMACAO_SEGUNDOS
        )

    async def load_session(self) -> bool:
        """Confirma o token no Xano e carrega usuário e status do onboarding."""
        if not self.token:
            return False
        if self.is_confirmation_recent():
            return True
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
        self._perfil = perfil
        self.erro_sessao = ""
        self._token_verificado = self.token
        self._verificada_em = time.monotonic()
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
        except XanoError as erro:
            self.erro_sessao = (
                MENSAGEM_LIMITE_REQUISICOES if erro.tipo == "limite_requisicoes" else MENSAGEM_FALHA_SESSAO
            )
            return
        self.erro_sessao = ""
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
    def retry_session(self):
        """Botão "Tentar novamente" da tela de erro: recarrega a página e refaz todos os on_load."""
        self.erro_sessao = ""
        return rx.call_script("window.location.reload()")

    @rx.event
    def logout(self):
        self.clear_session()
        return rx.redirect("/")

    @rx.event
    def redirect_to_perfil(self):
        return rx.redirect(ROTA_PERFIL)
