"""Formulário da tela de Perfil: carregar, editar e salvar no Xano."""

from datetime import date

import reflex as rx

from projetofacul.logic.navegacao import ROTA_INICIO, ROTA_LOGIN
from projetofacul.logic.perfil_validacao import (
    build_form_from_perfil,
    build_perfil_payload,
    validate_perfil,
)
from projetofacul.services import xano_client
from projetofacul.services.xano_client import XanoError
from projetofacul.states.sessao_state import SessaoState

MENSAGEM_FALHA_SALVAR = "Não foi possível salvar seu perfil agora. Tente novamente em instantes."

# só estes campos podem ser alterados pelo evento genérico vindo do navegador
CAMPOS_TEXTO = (
    "nome",
    "data_de_nascimento",
    "sexo",
    "altura_cm",
    "tipo_fisico",
    "nivel_fisico",
    "horario_fav_de_treino",
    "meta_semanal",
    "objetivo",
)


class PerfilState(rx.State):
    """Valores do formulário de Perfil, erros por campo e estado de envio."""

    nome: str = ""
    data_de_nascimento: str = ""
    sexo: str = ""
    altura_cm: str = ""
    tipo_fisico: str = ""
    nivel_fisico: str = ""
    horario_fav_de_treino: str = ""
    meta_semanal: str = ""
    objetivo: str = ""
    modalidade_fav1: list[str] = []
    erros: dict[str, str] = {}
    erro_geral: str = ""
    salvando: bool = False
    # sem campo na tela nesta versão; reenviado como veio do Xano
    _medidas: bool = False

    def fill_form(self, perfil: dict):
        for campo, valor in build_form_from_perfil(perfil).items():
            setattr(self, campo, valor)
        self._medidas = bool(perfil.get("medidas"))
        self.erros = {}
        self.erro_geral = ""

    def get_form_data(self) -> dict:
        dados = {campo: getattr(self, campo) for campo in CAMPOS_TEXTO}
        dados["modalidade_fav1"] = list(self.modalidade_fav1)
        return dados

    def clear_error(self, campo: str):
        if campo in self.erros:
            self.erros = {chave: valor for chave, valor in self.erros.items() if chave != campo}

    @rx.event
    async def load_profile(self):
        """on_load de /perfil, depois do guarda de sessão que já leu o Perfil."""
        sessao = await self.get_state(SessaoState)
        if sessao.sessao_verificada:
            self.fill_form(sessao._perfil)

    @rx.event
    def update_field(self, campo: str, valor: str):
        if campo not in CAMPOS_TEXTO:
            return
        # inputs numéricos chegam do navegador como número; o formulário guarda tudo como texto
        setattr(self, campo, "" if valor is None else str(valor))
        self.clear_error(campo)

    @rx.event
    def toggle_modalidade(self, modalidade: str):
        if modalidade in self.modalidade_fav1:
            self.modalidade_fav1 = [item for item in self.modalidade_fav1 if item != modalidade]
        else:
            self.modalidade_fav1 = [*self.modalidade_fav1, modalidade]
        self.clear_error("modalidade_fav1")

    @rx.event
    async def save_profile(self):
        # proteção contra duplo clique
        if self.salvando:
            return

        dados = self.get_form_data()
        self.erro_geral = ""
        self.erros = validate_perfil(dados, date.today())
        if self.erros:
            return

        self.salvando = True
        yield

        sessao = await self.get_state(SessaoState)
        try:
            perfil = await xano_client.update_perfil(
                sessao.token, build_perfil_payload(dados, self._medidas)
            )
        except XanoError as erro:
            self.salvando = False
            if erro.tipo == "nao_autorizado":
                sessao.clear_session()
                yield rx.redirect(ROTA_LOGIN)
                return
            self.erro_geral = MENSAGEM_FALHA_SALVAR
            return

        estava_em_onboarding = not sessao.onboarding_concluido
        sessao.onboarding_concluido = True
        if isinstance(perfil, dict):
            sessao._perfil = perfil
        self.salvando = False
        yield rx.toast.success("Perfil salvo")
        if estava_em_onboarding:
            yield rx.redirect(ROTA_INICIO)
