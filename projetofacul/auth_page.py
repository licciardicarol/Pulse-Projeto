"""Tela única de autenticação do Pulse."""

from typing import Any

import reflex as rx

from projetofacul.logic.conta_validacao import (
    TAMANHO_MINIMO_SENHA,
    is_valid_email,
    is_valid_password,
    normalize_email,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError
from projetofacul.states.sessao_state import SessaoState
from styles.theme import THEME

MENSAGEM_FALHA_GENERICA = "Não foi possível concluir o acesso agora. Tente novamente em instantes."


def get_auth_error_message(modo: str, tipo_erro: str) -> str:
    """Traduz o tipo de falha do Xano em mensagem amigável, sem detalhes técnicos."""
    if tipo_erro == "nao_configurado":
        return "O acesso está temporariamente indisponível."
    if modo == "cadastro":
        if tipo_erro == "acesso_negado":
            # não confirma que o e-mail existe; apenas orienta para o login
            return "Não foi possível criar a conta com este e-mail. Se você já tem conta, use Entrar."
        if tipo_erro == "invalido":
            return "Verifique os dados informados e tente novamente."
        return MENSAGEM_FALHA_GENERICA
    if tipo_erro in ("acesso_negado", "nao_autorizado", "invalido"):
        return "E-mail ou senha incorretos."
    return MENSAGEM_FALHA_GENERICA


class AuthState(rx.State):
    """Controla modo, validação e envio da tela de autenticação."""

    modo: str = "login"
    nome: str = ""
    email: str = ""
    senha: str = ""
    confirmar_senha: str = ""
    mostrar_senha: bool = False
    mostrar_confirmacao: bool = False
    erro_nome: str = ""
    erro_email: str = ""
    erro_senha: str = ""
    erro_confirmacao: str = ""
    erro_geral: str = ""
    enviando: bool = False

    @rx.event
    def inicializar_login(self):
        self.modo = "login"
        self.limpar_erros()

    @rx.event
    def inicializar_cadastro(self):
        self.modo = "cadastro"
        self.limpar_erros()

    @rx.event
    def trocar_modo(self, modo: str):
        self.modo = modo
        self.senha = ""
        self.confirmar_senha = ""
        self.mostrar_senha = False
        self.mostrar_confirmacao = False
        self.limpar_erros()
        return rx.redirect("/cadastro" if modo == "cadastro" else "/login")

    @rx.event
    def atualizar_campo(self, campo: str, valor: str):
        setattr(self, campo, valor)
        if campo == "email":
            self.erro_email = ""
        elif campo == "nome":
            self.erro_nome = ""
        elif campo == "senha":
            self.erro_senha = ""
            self.erro_confirmacao = ""
        elif campo == "confirmar_senha":
            self.erro_confirmacao = ""

    @rx.event
    def alternar_visibilidade(self, campo: str):
        if campo == "confirmacao":
            self.mostrar_confirmacao = not self.mostrar_confirmacao
        else:
            self.mostrar_senha = not self.mostrar_senha

    @rx.event
    def recuperar_senha(self):
        self.erro_geral = "A recuperação de senha ainda não está disponível."

    @rx.event
    async def enviar(self, form_data: dict[str, Any]):
        # proteção contra duplo envio (Enter + clique, cliques repetidos)
        if self.enviando:
            return

        self.nome = form_data.get("nome", "").strip()
        self.email = form_data.get("email", "").strip()
        self.senha = form_data.get("senha", "")
        self.confirmar_senha = form_data.get("confirmar_senha", "")
        self.limpar_erros()

        if self.modo == "cadastro" and not self.nome:
            self.erro_nome = "Informe seu nome completo."
        elif self.modo == "cadastro" and len(self.nome) > 50:
            self.erro_nome = "Use no máximo 50 caracteres."

        if not is_valid_email(self.email):
            self.erro_email = "Informe um e-mail válido."

        if not is_valid_password(self.senha):
            self.erro_senha = f"A senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."

        if self.modo == "cadastro" and self.confirmar_senha != self.senha:
            self.erro_confirmacao = "As senhas não coincidem."

        if any((self.erro_nome, self.erro_email, self.erro_senha, self.erro_confirmacao)):
            return

        self.enviando = True
        yield

        try:
            if self.modo == "cadastro":
                token = await xano_client.signup(self.nome, normalize_email(self.email), self.senha)
            else:
                token = await xano_client.login(normalize_email(self.email), self.senha)
        except XanoError as erro:
            self.erro_geral = get_auth_error_message(self.modo, erro.tipo)
            self.enviando = False
            return

        sessao = await self.get_state(SessaoState)
        destino = await sessao.start_session(token)
        self.senha = ""
        self.confirmar_senha = ""
        self.enviando = False
        yield rx.redirect(destino)

    def limpar_erros(self):
        self.erro_nome = ""
        self.erro_email = ""
        self.erro_senha = ""
        self.erro_confirmacao = ""
        self.erro_geral = ""


AUTH_PAGE_CSS = """
html, body, #root { min-height: 100%; margin: 0; }
.auth-page {
  min-height: 100vh;
  color: __TEXT__;
  background: linear-gradient(135deg, __HERO_START__ 0%, __HERO_MIDDLE__ 55%, __HERO_END__ 100%);
  font-family: __FONT__;
  box-sizing: border-box;
}
.auth-page *, .auth-page *::before, .auth-page *::after { box-sizing: border-box; }
.auth-layout {
  width: min(1200px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 40px 28px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 520px);
  gap: clamp(44px, 7vw, 104px);
  align-items: center;
}
.auth-intro, .auth-panel { animation: auth-rise 520ms cubic-bezier(.2,.8,.2,1) both; }
.auth-panel { width: 100%; max-width: 520px; justify-self: end; animation-delay: 80ms; }
.auth-brand { display: flex; align-items: center; gap: 11px; margin-bottom: 26px; }
.auth-brand-mark {
  width: 42px; height: 42px; display: grid; place-items: center;
  border-radius: 13px; background: __PRIMARY__; box-shadow: 0 8px 18px rgba(43,140,255,.24);
}
.auth-brand-name { font-size: 22px; line-height: 1; font-weight: 800; }
.auth-brand-mobile { display: none; }
.auth-title {
    max-width: 650px; margin: 0 0 18px; font-size: 50px;
    line-height: 1.1; letter-spacing: 0; font-weight: 800;
}
.auth-subtitle { max-width: 620px; margin: 0; color: __SECONDARY__; font-size: 16px; line-height: 1.75; }
.auth-benefits { display: grid; gap: 21px; margin-top: 36px; }
.auth-benefit { display: grid; grid-template-columns: 48px minmax(0,1fr); gap: 15px; align-items: center; }
.auth-benefit-icon {
  width: 48px; height: 48px; display: grid; place-items: center; border-radius: 14px;
  color: __PRIMARY__; background: rgba(43,140,255,.13); border: 1px solid rgba(59,147,255,.18);
}
.auth-benefit-title { margin: 0 0 4px; font-size: 15px; font-weight: 700; }
.auth-benefit-copy { margin: 0; color: __SECONDARY__; font-size: 13px; line-height: 1.55; }
.auth-form-card {
  padding: 32px; border: 1px solid __BORDER__; border-radius: 20px;
  background: __SURFACE__; box-shadow: 0 24px 64px rgba(0,0,0,.28);
}
.auth-google {
  width: 100%; min-height: 48px; display: flex; align-items: center; justify-content: center; gap: 11px;
  border: 1px solid rgba(255,255,255,.14); border-radius: 10px; background: rgba(255,255,255,.035);
  color: __TEXT__; font: inherit; font-size: 14px; font-weight: 650;
}
.auth-google:disabled { opacity: .68; cursor: not-allowed; }
.auth-google-mark { color: #82B7FF; font-size: 18px; font-weight: 800; }
.auth-divider { display: flex; align-items: center; gap: 13px; margin: 23px 0; color: __MUTED__; font-size: 12px; white-space: nowrap; }
.auth-divider::before, .auth-divider::after { content: ""; height: 1px; flex: 1; background: rgba(255,255,255,.1); }
.auth-tabs {
  position: relative; isolation: isolate; display: grid; grid-template-columns: 1fr 1fr; gap: 4px;
    min-height: 52px; padding: 4px; margin-bottom: 23px; border-radius: 11px; background: rgba(4,11,23,.55);
}
.auth-tabs::before {
  content: ""; position: absolute; z-index: -1; top: 4px; bottom: 4px; left: 4px; width: calc(50% - 4px);
  border-radius: 8px; background: #1A2940; box-shadow: 0 2px 8px rgba(0,0,0,.22);
  transition: transform 200ms ease;
}
.auth-tabs.is-signup::before { transform: translateX(100%); }
.auth-tab {
    min-height: 44px; padding: 0 10px; border: 0; border-radius: 8px; color: __SECONDARY__;
  background: transparent; font: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: color 180ms ease, transform 160ms ease;
}
.auth-tab[aria-selected="true"] { color: __TEXT__; }
.auth-tab:active { transform: scale(.98); }
.auth-tab:focus-visible, .auth-button:focus-visible, .auth-eye:focus-visible, .auth-forgot:focus-visible, .auth-back:focus-visible {
  outline: 3px solid rgba(43,140,255,.65); outline-offset: 3px;
}
.auth-form { display: grid; gap: 16px; }
.auth-field { display: grid; gap: 8px; min-width: 0; }
.auth-label-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.auth-label { color: #E8EEF8; font-size: 13px; font-weight: 650; }
.auth-forgot { min-height: 44px; padding: 0; border: 0; background: transparent; color: #8EBEFF; font: inherit; font-size: 12px; cursor: pointer; }
.auth-forgot:hover { color: #BEDAFF; text-decoration: underline; }
.auth-input-wrap { position: relative; min-width: 0; }
.auth-input {
  width: 100%; min-height: 46px; padding: 0 14px; border: 1px solid rgba(255,255,255,.12); border-radius: 9px;
  outline: none; color: __TEXT__; background: rgba(5,12,24,.54); font: inherit; font-size: 14px;
  transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
}
.auth-input::placeholder { color: #71829A; }
.auth-input:focus { border-color: __PRIMARY__; background: rgba(5,12,24,.72); box-shadow: 0 0 0 3px rgba(43,140,255,.18); }
.auth-input.has-eye { padding-right: 48px; }
.auth-input[aria-invalid="true"] { border-color: #D6818B; }
.auth-field.has-error .auth-input { animation: auth-shake 240ms ease-in-out; }
.auth-eye {
    position: absolute; top: 1px; right: 1px; width: 44px; height: 44px; display: grid; place-items: center;
  border: 0; border-radius: 7px; color: __SECONDARY__; background: transparent; cursor: pointer;
}
.auth-eye:hover { color: __TEXT__; background: rgba(255,255,255,.07); }
.auth-error { margin: 0; color: #F0A1A9; font-size: 12px; line-height: 1.4; }
.auth-global-error { margin: 0; padding: 11px 12px; border: 1px solid rgba(240,161,169,.24); border-radius: 8px; color: #F2B1B7; background: rgba(130,35,48,.15); font-size: 13px; line-height: 1.5; }
.auth-expanding { display: grid; grid-template-rows: 0fr; opacity: 0; overflow: hidden; transition: grid-template-rows 200ms ease, opacity 200ms ease; }
.auth-expanding.is-open { grid-template-rows: 1fr; opacity: 1; }
.auth-expanding-inner { min-height: 0; overflow: hidden; display: grid; gap: 16px; }
.auth-button {
  min-height: 48px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 9px;
  margin-top: 2px; border: 0; border-radius: 10px; color: __TEXT__; background: __PRIMARY__;
  box-shadow: 0 10px 26px rgba(43,140,255,.18); font: inherit; font-size: 14px; font-weight: 750; cursor: pointer;
  transition: transform 170ms ease, box-shadow 170ms ease, background 170ms ease, opacity 170ms ease;
}
.auth-button:hover:not(:disabled) { transform: translateY(-1px); background: __PRIMARY_HOVER__; box-shadow: 0 14px 30px rgba(43,140,255,.26); }
.auth-button:active:not(:disabled) { transform: scale(.98); }
.auth-button:disabled { opacity: .72; cursor: wait; }
.auth-privacy { margin: 20px 0 0; color: __MUTED__; font-size: 11px; line-height: 1.55; text-align: center; }
.auth-back { display: block; width: fit-content; margin: 20px auto 0; color: __SECONDARY__; font-size: 13px; text-decoration: none; }
.auth-back:hover { color: __TEXT__; text-decoration: underline; }
@keyframes auth-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes auth-shake { 25% { transform: translateX(-3px); } 75% { transform: translateX(3px); } }
@media (max-width: 900px) {
  .auth-layout { max-width: 640px; grid-template-columns: minmax(0,1fr); gap: 34px; padding: 30px 24px; }
  .auth-panel { order: -1; justify-self: center; }
  .auth-intro { order: 1; }
  .auth-brand-desktop { display: none; }
  .auth-brand-mobile { display: flex; margin-bottom: 18px; }
    .auth-title { font-size: 40px; }
  .auth-benefits { grid-template-columns: 1fr; gap: 15px; margin-top: 22px; }
}
@media (max-width: 520px) {
  .auth-layout { padding: 22px 16px 28px; gap: 27px; }
  .auth-form-card { padding: 22px 20px; border-radius: 17px; }
    .auth-title { font-size: 30px; }
  .auth-subtitle { font-size: 14px; }
  .auth-benefits { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .auth-intro, .auth-panel { animation: none; }
    .auth-page *, .auth-page *::before, .auth-page *::after {
        transition-duration: .01ms !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
    }
}
"""
for chave, valor in {
    "__TEXT__": THEME.COLORS["text_primary"],
    "__HERO_START__": THEME.COLORS["hero_start"],
    "__HERO_MIDDLE__": THEME.COLORS["hero_middle"],
    "__HERO_END__": THEME.COLORS["hero_end"],
    "__FONT__": THEME.FONT_FAMILIES,
    "__PRIMARY__": THEME.COLORS["primary"],
    "__PRIMARY_HOVER__": THEME.COLORS["primary_hover"],
    "__SECONDARY__": THEME.COLORS["text_secondary"],
    "__MUTED__": THEME.COLORS["text_muted"],
    "__SURFACE__": THEME.COLORS["surface"],
    "__BORDER__": THEME.COLORS["border"],
}.items():
    AUTH_PAGE_CSS = AUTH_PAGE_CSS.replace(chave, valor)


def auth_brand(class_name: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(tag="activity", size=21, color=THEME.COLORS["text_primary"]),
            class_name="auth-brand-mark",
        ),
        rx.text("Pulse", class_name="auth-brand-name"),
        class_name=f"auth-brand {class_name}",
        align="center",
    )


def auth_benefit(icon_name: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(rx.icon(tag=icon_name, size=20), class_name="auth-benefit-icon"),
        rx.vstack(
            rx.text(title, class_name="auth-benefit-title"),
            rx.text(description, class_name="auth-benefit-copy"),
            align="start",
            spacing="1",
        ),
        class_name="auth-benefit",
        align="center",
    )


def auth_field(label: str, input_id: str, input_component: rx.Component, erro) -> rx.Component:
    return rx.vstack(
        rx.el.label(label, html_for=input_id, class_name="auth-label"),
        input_component,
        rx.cond(
            erro != "",
            rx.text(erro, class_name="auth-error", role="alert", aria_live="polite"),
            rx.fragment(),
        ),
        class_name=rx.cond(erro != "", "auth-field has-error", "auth-field"),
        align="stretch",
        spacing="2",
        width="100%",
    )


def password_input(campo: str, input_id: str, valor, mostrar, autocomplete, desabilitado=False) -> rx.Component:
    nome_campo = "senha" if campo == "senha" else "confirmar_senha"
    return rx.box(
        rx.el.input(
            id=input_id,
            name=nome_campo,
            type=rx.cond(mostrar, "text", "password"),
            auto_complete=autocomplete,
            value=valor,
            on_change=lambda valor_campo: AuthState.atualizar_campo(nome_campo, valor_campo),
            placeholder="Mínimo de 8 caracteres" if campo == "senha" else "Digite a senha novamente",
            min_length=8 if campo == "senha" else None,
            disabled=desabilitado,
            aria_invalid=AuthState.erro_senha != "" if campo == "senha" else AuthState.erro_confirmacao != "",
            class_name="auth-input has-eye",
        ),
        rx.button(
            rx.cond(
                mostrar,
                rx.icon(tag="eye-off", size=17),
                rx.icon(tag="eye", size=17),
            ),
            type="button",
            title=rx.cond(mostrar, "Ocultar senha", "Mostrar senha"),
            aria_label=rx.cond(mostrar, "Ocultar senha", "Mostrar senha"),
            on_click=AuthState.alternar_visibilidade(campo),
            class_name="auth-eye",
        ),
        class_name="auth-input-wrap",
        width="100%",
    )


def pagina_autenticacao() -> rx.Component:
    return rx.box(
        rx.html(
            '<link rel="preconnect" href="https://fonts.googleapis.com" />'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />'
            '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />'
            f"<style>{AUTH_PAGE_CSS}</style>"
        ),
        rx.box(
            rx.box(
                auth_brand("auth-brand-desktop"),
                rx.heading(
                    "Seu treino, sua alimentação e seu descanso no mesmo lugar.",
                    class_name="auth-title",
                    as_="h1",
                ),
                rx.text(
                    "Registre em segundos e deixe a IA calcular calorias, analisar refeições e indicar a intensidade do próximo treino com base no seu sono.",
                    class_name="auth-subtitle",
                ),
                rx.vstack(
                    auth_benefit(
                        "brain-circuit",
                        "IA no cálculo",
                        "Calorias do treino e macros da refeição estimados automaticamente.",
                    ),
                    auth_benefit(
                        "chart-no-axes-combined",
                        "Evolução visível",
                        "Peso, medidas e frequência de treino em gráficos claros.",
                    ),
                    auth_benefit(
                        "shield-check",
                        "Privado por padrão",
                        "Seus registros são visíveis só para você.",
                    ),
                    class_name="auth-benefits",
                    align="stretch",
                    spacing="0",
                    width="100%",
                ),
                class_name="auth-intro",
            ),
            rx.box(
                auth_brand("auth-brand-mobile"),
                rx.box(
                    rx.button(
                        rx.text("G", class_name="auth-google-mark"),
                        "Continuar com Google",
                        type="button",
                        disabled=True,
                        title="Acesso com Google ainda não configurado",
                        class_name="auth-google",
                    ),
                    rx.text("ou use seu e-mail", class_name="auth-divider"),
                    rx.box(
                        rx.button(
                            "Entrar",
                            type="button",
                            role="tab",
                            aria_selected=AuthState.modo == "login",
                            aria_controls="auth-panel",
                            on_click=AuthState.trocar_modo("login"),
                            class_name="auth-tab",
                        ),
                        rx.button(
                            "Criar conta",
                            type="button",
                            role="tab",
                            aria_selected=AuthState.modo == "cadastro",
                            aria_controls="auth-panel",
                            on_click=AuthState.trocar_modo("cadastro"),
                            class_name="auth-tab",
                        ),
                        role="tablist",
                        aria_label="Tipo de acesso",
                        class_name=rx.cond(
                            AuthState.modo == "cadastro",
                            "auth-tabs is-signup",
                            "auth-tabs",
                        ),
                    ),
                    rx.form(
                        rx.box(
                            rx.box(
                                rx.box(
                                    rx.box(
                                        auth_field(
                                            "Nome completo",
                                            "auth-name",
                                            rx.el.input(
                                                id="auth-name",
                                                name="nome",
                                                type="text",
                                                auto_complete="name",
                                                value=AuthState.nome,
                                                on_change=lambda valor: AuthState.atualizar_campo("nome", valor),
                                                placeholder="Como quer ser chamado",
                                                disabled=AuthState.modo != "cadastro",
                                                aria_invalid=AuthState.erro_nome != "",
                                                class_name="auth-input",
                                            ),
                                            AuthState.erro_nome,
                                        ),
                                        auth_field(
                                            "Confirmar senha",
                                            "auth-confirm-password",
                                            password_input(
                                                "confirmacao",
                                                "auth-confirm-password",
                                                AuthState.confirmar_senha,
                                                AuthState.mostrar_confirmacao,
                                                "new-password",
                                                AuthState.modo != "cadastro",
                                            ),
                                            AuthState.erro_confirmacao,
                                        ),
                                        class_name="auth-expanding-inner",
                                    ),
                                    class_name=rx.cond(
                                        AuthState.modo == "cadastro",
                                        "auth-expanding is-open",
                                        "auth-expanding",
                                    ),
                                    aria_hidden=AuthState.modo != "cadastro",
                                ),
                                rx.box(
                                    auth_field(
                                        "E-mail",
                                        "auth-email",
                                        rx.el.input(
                                            id="auth-email",
                                            name="email",
                                            type="email",
                                            auto_complete="email",
                                            value=AuthState.email,
                                            on_change=lambda valor: AuthState.atualizar_campo("email", valor),
                                            placeholder="voce@exemplo.com",
                                            aria_invalid=AuthState.erro_email != "",
                                            class_name="auth-input",
                                        ),
                                        AuthState.erro_email,
                                    ),
                                    rx.box(
                                        rx.hstack(
                                            rx.el.label("Senha", html_for="auth-password", class_name="auth-label"),
                                            rx.cond(
                                                AuthState.modo == "login",
                                                rx.button(
                                                    "Esqueci minha senha",
                                                    type="button",
                                                    on_click=AuthState.recuperar_senha,
                                                    class_name="auth-forgot",
                                                ),
                                                rx.fragment(),
                                            ),
                                            class_name="auth-label-row",
                                        ),
                                        password_input(
                                            "senha",
                                            "auth-password",
                                            AuthState.senha,
                                            AuthState.mostrar_senha,
                                            rx.cond(AuthState.modo == "login", "current-password", "new-password"),
                                        ),
                                        rx.cond(
                                            AuthState.erro_senha != "",
                                            rx.text(
                                                AuthState.erro_senha,
                                                class_name="auth-error",
                                                role="alert",
                                                aria_live="polite",
                                            ),
                                            rx.fragment(),
                                        ),
                                        class_name=rx.cond(
                                            AuthState.erro_senha != "",
                                            "auth-field has-error",
                                            "auth-field",
                                        ),
                                        align="stretch",
                                        spacing="2",
                                    ),
                                            class_name="auth-form",
                                ),
                                class_name="auth-form",
                                width="100%",
                            ),
                            rx.cond(
                                AuthState.erro_geral != "",
                                rx.text(
                                    AuthState.erro_geral,
                                    class_name="auth-global-error",
                                    role="status",
                                    aria_live="polite",
                                ),
                                rx.fragment(),
                            ),
                            rx.button(
                                rx.cond(AuthState.enviando, rx.spinner(size="3"), rx.fragment()),
                                rx.cond(AuthState.modo == "login", "Entrar", "Criar conta"),
                                type="submit",
                                disabled=AuthState.enviando,
                                class_name="auth-button",
                            ),
                            width="100%",
                        ),
                        on_submit=AuthState.enviar,
                        no_validate=True,
                        id="auth-panel",
                        role="tabpanel",
                        class_name="auth-form",
                    ),
                    rx.text(
                        "Seus registros de treino, sono, peso e refeições são visíveis apenas para você.",
                        class_name="auth-privacy",
                    ),
                    class_name="auth-form-card",
                ),
                rx.link("← Voltar para a página inicial", href="/", class_name="auth-back"),
                class_name="auth-panel",
            ),
            class_name="auth-layout",
        ),
        class_name="auth-page",
        width="100%",
    )