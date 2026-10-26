import asyncio
from datetime import datetime

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.logic.peso import FUSO_BRASILIA
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states import peso_state
from projetofacul.states.peso_state import (
    MENSAGEM_FALHA_EXCLUIR,
    MENSAGEM_FALHA_LISTAR,
    MENSAGEM_FALHA_SALVAR,
    PesoState,
)
from projetofacul.states.sessao_state import SessaoState

AGORA = datetime(2026, 10, 23, 18, 5, tzinfo=FUSO_BRASILIA)


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados(monkeypatch):
    monkeypatch.setattr(peso_state, "now_brasilia", lambda: AGORA)
    raiz = State(_reflex_internal_init=True)
    peso = get_substate(raiz, PesoState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    return peso, sessao


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado com uma lista em memória; `falhas` força erros por função."""
    banco = {"lista": [], "falhas": {}, "chamadas": []}

    async def list_registros_peso(token):
        banco["chamadas"].append(("list", token))
        if "list" in banco["falhas"]:
            raise banco["falhas"]["list"]
        return list(banco["lista"])

    async def create_registro_peso(token, peso, data_horario):
        banco["chamadas"].append(("create", token, peso, data_horario))
        if "create" in banco["falhas"]:
            raise banco["falhas"]["create"]
        novo = {"id": len(banco["lista"]) + 1, "created_at": len(banco["lista"]) + 1, "peso": peso,
                "data_horario": data_horario, "user_id": 7}
        banco["lista"].append(novo)
        return novo

    async def delete_registro_peso(token, registro_id):
        banco["chamadas"].append(("delete", token, registro_id))
        if "delete" in banco["falhas"]:
            raise banco["falhas"]["delete"]
        banco["lista"] = [r for r in banco["lista"] if r["id"] != registro_id]
        return {"sucesso": True}

    monkeypatch.setattr(xano_client, "list_registros_peso", list_registros_peso)
    monkeypatch.setattr(xano_client, "create_registro_peso", create_registro_peso)
    monkeypatch.setattr(xano_client, "delete_registro_peso", delete_registro_peso)
    return banco


def run(evento) -> list:
    async def coletar():
        if hasattr(evento, "__aiter__"):
            return [item async for item in evento if item is not None]
        resultado = await evento if asyncio.iscoroutine(evento) else evento
        return [resultado] if resultado is not None else []

    return asyncio.run(coletar())


def has_toast(eventos: list, texto: str) -> bool:
    return any("__toast" in str(evento) and texto in str(evento) for evento in eventos)


def save(estado: PesoState, **campos) -> list:
    for campo, valor in {"data": "2026-10-23", "horario": "17:38", **campos}.items():
        PesoState.update_field.fn(estado, campo, valor)
    return run(PesoState.save_weight.fn(estado, {}))


def test_carregar_vazio_preenche_data_e_hora_de_agora(estados, xano):
    peso, _ = estados
    run(PesoState.start_page.fn(peso))

    assert peso.carregando is False
    assert peso.registros == []
    assert (peso.data, peso.horario, peso.hoje) == ("2026-10-23", "18:05", "2026-10-23")
    assert (peso.peso_atual, peso.variacao) == ("—", "—")


def test_sem_sessao_verificada_nao_chama_o_xano(estados, xano):
    peso, sessao = estados
    sessao.sessao_verificada = False

    run(PesoState.start_page.fn(peso))

    assert xano["chamadas"] == []


def test_falha_ao_listar_mostra_erro_amigavel(estados, xano):
    peso, _ = estados
    xano["falhas"]["list"] = XanoError("indisponivel")

    run(PesoState.start_page.fn(peso))

    assert peso.erro_lista == MENSAGEM_FALHA_LISTAR
    assert peso.carregando is False


def test_limite_do_xano_pede_para_aguardar(estados, xano):
    peso, _ = estados
    xano["falhas"]["list"] = XanoError("limite_requisicoes")

    run(PesoState.start_page.fn(peso))

    assert peso.erro_lista == MENSAGEM_LIMITE_REQUISICOES


def test_salvar_valido_registra_limpa_so_o_peso_e_avisa(estados, xano):
    peso, _ = estados

    eventos = save(peso, peso="70,0")

    assert ("create", "tok-123", 70.0, 1792787880000) in xano["chamadas"]
    assert peso.peso == ""
    assert (peso.data, peso.horario) == ("2026-10-23", "18:05")
    assert peso.registros == [{"id": "1", "peso": "70,0 kg", "data_hora": "23/10/2026 · 17:38"}]
    assert (peso.peso_atual, peso.variacao) == ("70,0 kg", "—")
    assert peso.salvando is False
    assert has_toast(eventos, "Peso registrado")


def test_segundo_registro_calcula_a_diferenca(estados, xano):
    peso, _ = estados
    save(peso, peso="70,0", horario="08:00")
    save(peso, peso="68,8", horario="17:38")

    assert (peso.peso_atual, peso.variacao) == ("68,8 kg", "-1,2 kg")
    assert [item["peso"] for item in peso.registros] == ["68,8 kg", "70,0 kg"]


def test_salvar_invalido_nao_chama_o_xano(estados, xano):
    peso, _ = estados

    save(peso, peso="19,9", horario="18:30")

    assert xano["chamadas"] == []
    assert set(peso.erros) == {"peso", "horario"}


def test_falha_ao_salvar_mantem_o_peso_digitado(estados, xano):
    peso, _ = estados
    xano["falhas"]["create"] = XanoError("indisponivel")

    save(peso, peso="70,5")

    assert peso.erro_geral == MENSAGEM_FALHA_SALVAR
    assert peso.peso == "70,5"
    assert peso.salvando is False


def test_salvar_em_andamento_ignora_segundo_envio(estados, xano):
    peso, _ = estados
    peso.salvando = True

    save(peso, peso="70,5")

    assert xano["chamadas"] == []


def test_campo_fora_da_lista_e_ignorado(estados):
    peso, _ = estados
    PesoState.update_field.fn(peso, "salvando", "true")
    assert peso.salvando is False


def test_excluir_ultimo_registro_volta_ao_vazio(estados, xano):
    peso, _ = estados
    save(peso, peso="70,0")
    PesoState.ask_delete.fn(peso, "1")

    eventos = run(PesoState.confirm_delete.fn(peso))

    assert peso.registros == []
    assert (peso.peso_atual, peso.variacao) == ("—", "—")
    assert peso.exclusao_id == ""
    assert has_toast(eventos, "Registro excluído")


def test_cancelar_exclusao_nao_apaga(estados, xano):
    peso, _ = estados
    save(peso, peso="70,0")
    PesoState.ask_delete.fn(peso, "1")

    PesoState.set_delete_open.fn(peso, False)

    assert peso.exclusao_id == ""
    assert not [chamada for chamada in xano["chamadas"] if chamada[0] == "delete"]


def test_falha_ao_excluir_mantem_item(estados, xano):
    peso, _ = estados
    save(peso, peso="70,0")
    xano["falhas"]["delete"] = XanoError("indisponivel")
    PesoState.ask_delete.fn(peso, "1")

    eventos = run(PesoState.confirm_delete.fn(peso))

    assert len(peso.registros) == 1
    assert has_toast(eventos, MENSAGEM_FALHA_EXCLUIR)


def test_sessao_expirada_ao_listar_vai_para_login(estados, xano):
    peso, sessao = estados
    xano["falhas"]["list"] = XanoError("nao_autorizado")

    eventos = run(PesoState.start_page.fn(peso))

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)
