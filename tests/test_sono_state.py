import asyncio
from datetime import datetime, timezone

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.logic.sono_registro import parse_local_datetime, to_utc_ms
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states import sono_state
from projetofacul.states.sessao_state import SessaoState
from projetofacul.states.sono_state import (
    MENSAGEM_CONFLITO_SERVIDOR,
    MENSAGEM_FALHA_EXCLUIR,
    MENSAGEM_FALHA_LISTAR,
    MENSAGEM_FALHA_SALVAR,
    SonoState,
)

BRASILIA = 180
# 21/10/2026 12:00 em Brasília
AGORA = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)


def ms(texto: str) -> int:
    return to_utc_ms(parse_local_datetime(texto), BRASILIA)


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados(monkeypatch):
    monkeypatch.setattr(sono_state, "get_now", lambda: AGORA)
    raiz = State(_reflex_internal_init=True)
    sono = get_substate(raiz, SonoState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    return sono, sessao


@pytest.fixture
def xano(monkeypatch):
    """Xano simulado com uma lista em memória; `falhas` força erros por função."""
    banco = {"lista": [], "falhas": {}, "chamadas": []}

    async def list_sono(token):
        banco["chamadas"].append(("list", token))
        if "list" in banco["falhas"]:
            raise banco["falhas"]["list"]
        return list(banco["lista"])

    async def create_sono(token, inicio_sono, fim_sono, qualidade_sono, observacoes):
        banco["chamadas"].append(("create", token, inicio_sono, fim_sono, qualidade_sono, observacoes))
        if "create" in banco["falhas"]:
            raise banco["falhas"]["create"]
        novo = {"id": 100 + len(banco["lista"]), "inicio_sono": inicio_sono, "fim_sono": fim_sono,
                "qualidade_sono": qualidade_sono, "observacoes": observacoes,
                "duracao_minutos": (fim_sono - inicio_sono) // 60000}
        banco["lista"].append(novo)
        return novo

    async def update_sono(token, sono_id, inicio_sono, fim_sono, qualidade_sono, observacoes):
        banco["chamadas"].append(("update", token, sono_id, inicio_sono, fim_sono, qualidade_sono, observacoes))
        if "update" in banco["falhas"]:
            raise banco["falhas"]["update"]
        atualizado = {"id": sono_id, "inicio_sono": inicio_sono, "fim_sono": fim_sono,
                      "qualidade_sono": qualidade_sono, "observacoes": observacoes}
        banco["lista"] = [atualizado if r["id"] == sono_id else r for r in banco["lista"]]
        return atualizado

    async def delete_sono(token, sono_id):
        banco["chamadas"].append(("delete", token, sono_id))
        if "delete" in banco["falhas"]:
            raise banco["falhas"]["delete"]
        banco["lista"] = [r for r in banco["lista"] if r["id"] != sono_id]
        return {"sucesso": True}

    for nome, funcao in (("list_sono", list_sono), ("create_sono", create_sono),
                         ("update_sono", update_sono), ("delete_sono", delete_sono)):
        monkeypatch.setattr(xano_client, nome, funcao)
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


def chamadas(xano, tipo: str) -> list:
    return [c for c in xano["chamadas"] if c[0] == tipo]


def noite(id_, inicio="2026-10-20T23:00", fim="2026-10-21T07:00", qualidade=3) -> dict:
    return {"id": id_, "inicio_sono": ms(inicio), "fim_sono": ms(fim), "qualidade_sono": qualidade,
            "observacoes": None, "duracao_minutos": (ms(fim) - ms(inicio)) // 60000}


def load(sono) -> list:
    return run(SonoState.start_page.fn(sono))


def fill(sono, inicio="2026-10-20T23:00", fim="2026-10-21T07:00", qualidade=4):
    SonoState.update_field.fn(sono, "inicio_sono", inicio)
    SonoState.update_field.fn(sono, "fim_sono", fim)
    if qualidade:
        SonoState.select_qualidade.fn(sono, qualidade)


def test_carregar_sem_registros_deixa_formulario_livre(estados, xano):
    sono, _ = estados
    load(sono)

    assert sono.carregando is False
    assert sono.registros == []
    # data e hora livres: nada vem preenchido
    assert sono.inicio_sono == "" and sono.fim_sono == ""
    assert sono.qualidade_sono == 0
    assert sono.duracao_texto == "—"
    assert sono.pode_salvar is False
    # sem tentar salvar, campo vazio não vira mensagem de erro
    assert sono.erros == {}


def test_limite_do_calendario_e_agora_em_brasilia(estados, xano):
    sono, _ = estados
    load(sono)
    assert sono.limite_maximo == "2026-10-21T12:00"


def test_carregar_ordena_e_exibe_em_brasilia(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(18, "2026-10-17T23:00", "2026-10-18T07:00"), noite(20, "2026-10-19T23:00", "2026-10-20T07:00"),
                     noite(19, "2026-10-18T23:00", "2026-10-19T07:00")]
    load(sono)

    assert [r["id"] for r in sono.registros] == ["20", "19", "18"]
    assert sono.registros[0]["intervalo"] == "19/10 23:00 → 20/10 07:00"
    assert sono.registros[0]["data"] == "20/10/2026"


def test_falha_ao_listar_mostra_erro_amigavel(estados, xano):
    sono, _ = estados
    xano["falhas"]["list"] = XanoError("indisponivel")
    load(sono)

    assert sono.erro_lista == MENSAGEM_FALHA_LISTAR
    assert sono.carregando is False


def test_limite_do_xano_ao_listar_pede_para_aguardar(estados, xano):
    sono, _ = estados
    xano["falhas"]["list"] = XanoError("limite_requisicoes")
    load(sono)
    assert sono.erro_lista == MENSAGEM_LIMITE_REQUISICOES


def test_sessao_expirada_ao_listar_vai_para_login(estados, xano):
    sono, sessao = estados
    xano["falhas"]["list"] = XanoError("nao_autorizado")

    eventos = load(sono)

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)


def test_duracao_e_botao_mudam_ao_preencher_campos(estados, xano):
    sono, _ = estados
    load(sono)

    SonoState.update_field.fn(sono, "inicio_sono", "2026-10-20T23:30")
    assert sono.duracao_texto == "—"
    SonoState.update_field.fn(sono, "fim_sono", "2026-10-21T07:00")
    assert sono.duracao_texto == "7h 30min"
    assert sono.pode_salvar is False

    SonoState.select_qualidade.fn(sono, 4)
    assert sono.pode_salvar is True

    SonoState.update_field.fn(sono, "fim_sono", "2026-10-20T22:00")
    assert sono.duracao_texto == "—"
    assert sono.erros["fim_sono"] == "O fim do sono precisa ser depois do início."
    assert sono.pode_salvar is False


def test_selecao_unica_de_qualidade(estados, xano):
    sono, _ = estados
    load(sono)
    SonoState.select_qualidade.fn(sono, 4)
    SonoState.select_qualidade.fn(sono, 2)
    assert sono.qualidade_sono == 2


def test_fim_no_futuro_bloqueia(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, inicio="2026-10-21T10:00", fim="2026-10-21T13:00")

    assert sono.erros["fim_sono"] == "O fim do sono não pode estar no futuro."
    assert sono.pode_salvar is False


def test_observacoes_cortadas_em_500(estados, xano):
    sono, _ = estados
    SonoState.update_field.fn(sono, "observacoes", "a" * 600)
    assert len(sono.observacoes) == 500


def test_salvar_vazio_mostra_obrigatorios_e_nao_chama_o_xano(estados, xano):
    sono, _ = estados
    load(sono)

    run(SonoState.save_sono.fn(sono))

    assert chamadas(xano, "create") == []
    assert sono.erros == {
        "inicio_sono": "Informe o início do sono.",
        "fim_sono": "Informe o fim do sono.",
        "qualidade_sono": "Selecione a qualidade do sono.",
    }


def test_primeiro_registro_aparece_e_formulario_fica_livre_de_novo(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, inicio="2026-10-20T23:30")
    SonoState.update_field.fn(sono, "observacoes", "  Acordei 2x  ")

    eventos = run(SonoState.save_sono.fn(sono))

    # 20/10 23:30 em Brasília é 21/10 02:30 UTC
    assert chamadas(xano, "create") == [
        ("create", "tok-123", ms("2026-10-20T23:30"), ms("2026-10-21T07:00"), 4, "Acordei 2x")
    ]
    assert len(sono.registros) == 1
    assert sono.registros[0]["duracao"] == "7h 30min"
    assert has_toast(eventos, "Sono registrado com sucesso")
    assert sono.inicio_sono == "" and sono.fim_sono == ""
    assert sono.qualidade_sono == 0 and sono.observacoes == ""
    assert sono.erros == {}
    assert sono.salvando is False
    # a resposta do POST entra na lista sem buscar de novo
    assert len(chamadas(xano, "list")) == 1


def test_novo_registro_entra_no_topo(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(1, "2026-10-18T23:00", "2026-10-19T07:00")]
    load(sono)
    fill(sono, qualidade=5)

    run(SonoState.save_sono.fn(sono))

    assert [r["data"] for r in sono.registros] == ["21/10/2026", "19/10/2026"]


def test_soneca_no_mesmo_dia(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, inicio="2026-10-21T10:00", fim="2026-10-21T10:40", qualidade=3)

    run(SonoState.save_sono.fn(sono))

    assert sono.registros[0]["intervalo"] == "10:00 → 10:40"
    assert sono.registros[0]["duracao"] == "40min"


def test_conflito_local_nao_envia_e_mostra_periodo(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(1, "2026-10-20T23:00", "2026-10-21T07:00")]
    load(sono)
    fill(sono, inicio="2026-10-21T06:00", fim="2026-10-21T08:00", qualidade=3)

    run(SonoState.save_sono.fn(sono))

    assert chamadas(xano, "create") == []
    assert sono.erro_geral == "Já existe um registro de sono nesse período (20/10 23:00 → 21/10 07:00). Ajuste os horários."
    assert sono.erro_permite_repetir is False


def test_periodo_encostado_e_salvo(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(1, "2026-10-20T23:00", "2026-10-21T07:00")]
    load(sono)
    fill(sono, inicio="2026-10-21T07:00", fim="2026-10-21T08:00", qualidade=3)

    run(SonoState.save_sono.fn(sono))

    assert len(chamadas(xano, "create")) == 1


def test_conflito_no_servidor_recarrega_lista(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, qualidade=3)
    xano["falhas"]["create"] = XanoError("invalido")

    run(SonoState.save_sono.fn(sono))

    assert sono.erro_geral == MENSAGEM_CONFLITO_SERVIDOR
    assert len(chamadas(xano, "list")) == 2


def test_falha_do_servidor_mantem_campos_e_oferece_tentar_de_novo(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, qualidade=2)
    SonoState.update_field.fn(sono, "observacoes", "Cafeína")
    xano["falhas"]["create"] = XanoError("indisponivel")

    run(SonoState.save_sono.fn(sono))

    assert sono.erro_geral == MENSAGEM_FALHA_SALVAR
    assert sono.erro_permite_repetir is True
    assert sono.inicio_sono == "2026-10-20T23:00"
    assert sono.qualidade_sono == 2 and sono.observacoes == "Cafeína"
    assert sono.registros == []
    assert sono.salvando is False

    # "Tentar novamente" refaz o envio com os mesmos dados
    del xano["falhas"]["create"]
    run(SonoState.save_sono.fn(sono))
    assert len(sono.registros) == 1


def test_salvar_em_andamento_ignora_segundo_clique(estados, xano):
    sono, _ = estados
    load(sono)
    fill(sono, qualidade=3)
    sono.salvando = True

    run(SonoState.save_sono.fn(sono))

    assert chamadas(xano, "create") == []


def test_sessao_expirada_ao_salvar_vai_para_login(estados, xano):
    sono, sessao = estados
    load(sono)
    fill(sono, qualidade=3)
    xano["falhas"]["create"] = XanoError("nao_autorizado")

    eventos = run(SonoState.save_sono.fn(sono))

    assert sessao.token == ""
    assert any("/login" in str(evento) for evento in eventos)


def test_editar_so_a_qualidade_ignora_o_proprio_periodo(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(7, qualidade=2)]
    load(sono)

    SonoState.start_edit.fn(sono, "7")
    assert sono.editando_id == "7"
    assert sono.qualidade_sono == 2
    assert sono.inicio_sono == "2026-10-20T23:00"
    assert sono.fim_sono == "2026-10-21T07:00"

    SonoState.select_qualidade.fn(sono, 5)
    eventos = run(SonoState.save_sono.fn(sono))

    assert chamadas(xano, "update")[0][:3] == ("update", "tok-123", 7)
    assert sono.registros[0]["rotulo_qualidade"] == "Muito bom"
    assert len(sono.registros) == 1
    assert sono.editando_id == ""
    assert has_toast(eventos, "Registro de sono atualizado")


def test_cancelar_edicao_limpa_formulario(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(7, "2026-10-19T22:00", "2026-10-20T06:00", qualidade=2)]
    load(sono)
    SonoState.start_edit.fn(sono, "7")

    SonoState.cancel_edit.fn(sono)

    assert sono.editando_id == ""
    assert sono.inicio_sono == "" and sono.qualidade_sono == 0
    assert chamadas(xano, "update") == []


def test_excluir_confirmado_remove_e_avisa(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(3)]
    load(sono)

    SonoState.ask_delete.fn(sono, "3")
    eventos = run(SonoState.confirm_delete.fn(sono))

    assert ("delete", "tok-123", 3) in xano["chamadas"]
    assert sono.registros == []
    assert sono.exclusao_id == ""
    assert has_toast(eventos, "Registro de sono excluído")


def test_excluir_registro_em_edicao_volta_ao_novo(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(3)]
    load(sono)
    SonoState.start_edit.fn(sono, "3")

    SonoState.ask_delete.fn(sono, "3")
    run(SonoState.confirm_delete.fn(sono))

    assert sono.editando_id == ""


def test_cancelar_exclusao_nao_apaga(estados, xano):
    sono, _ = estados
    SonoState.ask_delete.fn(sono, "3")
    SonoState.set_delete_open.fn(sono, False)

    assert sono.exclusao_id == ""
    assert chamadas(xano, "delete") == []


def test_falha_ao_excluir_mantem_item(estados, xano):
    sono, _ = estados
    xano["lista"] = [noite(3)]
    load(sono)
    xano["falhas"]["delete"] = XanoError("indisponivel")

    SonoState.ask_delete.fn(sono, "3")
    eventos = run(SonoState.confirm_delete.fn(sono))

    assert len(sono.registros) == 1
    assert has_toast(eventos, MENSAGEM_FALHA_EXCLUIR)
