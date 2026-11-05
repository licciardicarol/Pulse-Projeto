import asyncio
from datetime import date, datetime, timedelta, timezone

import pytest
from reflex.state import State

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.services import xano_client
from projetofacul.services.xano_client import MENSAGEM_LIMITE_REQUISICOES, XanoError
from projetofacul.states import relatorios_state
from projetofacul.states.relatorios_state import MENSAGENS_FALHA, RelatoriosState
from projetofacul.states.sessao_state import SessaoState

HOJE = date(2026, 11, 4)
BRASILIA = timezone(timedelta(hours=-3))


def ms(ano, mes, dia, hora=0, minuto=0) -> int:
    """Instante em horário de Brasília -> milissegundos UTC, como o Xano devolve."""
    return int(datetime(ano, mes, dia, hora, minuto, tzinfo=BRASILIA).timestamp() * 1000)


LISTAS = {
    "list_treinos": [{"data": "2026-11-02"}, {"data": "2026-10-28"}],
    "list_sono": [{"inicio_sono": ms(2026, 11, 3, 23), "fim_sono": ms(2026, 11, 4, 6, 30), "duracao_minutos": 450}],
    "list_registros_peso": [
        {"peso": 72.4, "data_horario": ms(2026, 10, 1, 8)},
        {"peso": 71.8, "data_horario": ms(2026, 11, 1, 8)},
    ],
    "list_refeicoes": [{"data_refeicao": "2026-11-03", "calorias": 650, "analise_ia": "ok"}],
}


def get_substate(raiz: State, classe):
    return raiz.get_substate(classe.get_full_name().split(".")[1:])


@pytest.fixture
def estados(monkeypatch):
    monkeypatch.setattr(relatorios_state, "get_today_sao_paulo", lambda: HOJE)
    raiz = State(_reflex_internal_init=True)
    relatorios = get_substate(raiz, RelatoriosState)
    sessao = get_substate(raiz, SessaoState)
    sessao.token = "tok-123"
    sessao.sessao_verificada = True
    return relatorios, sessao


@pytest.fixture
def xano(monkeypatch):
    """Simula as 4 listagens; `respostas[nome]` pode ser uma lista ou um XanoError."""
    respostas = {nome: list(lista) for nome, lista in LISTAS.items()}
    chamadas: list[tuple[str, str]] = []

    def simular(nome):
        async def listar(token):
            chamadas.append((nome, token))
            if isinstance(respostas[nome], Exception):
                raise respostas[nome]
            return respostas[nome]

        return listar

    for nome in LISTAS:
        monkeypatch.setattr(xano_client, nome, simular(nome))
    return respostas, chamadas


def run_start(relatorios: RelatoriosState) -> list:
    async def coletar():
        return [evento async for evento in RelatoriosState.start_page.fn(relatorios) if evento is not None]

    return asyncio.run(coletar())


def get_redirects(eventos: list) -> list[str]:
    destinos = []
    for evento in eventos:
        for nome, valor in getattr(evento, "args", ()):
            if nome._js_expr == "path":
                destinos.append(valor._var_value)
    return destinos


def test_carrega_as_quatro_series_em_sequencia(estados, xano):
    relatorios, _ = estados
    _, chamadas = xano

    eventos = run_start(relatorios)

    assert [nome for nome, _ in chamadas] == ["list_treinos", "list_sono", "list_registros_peso", "list_refeicoes"]
    assert all(token == "tok-123" for _, token in chamadas)
    assert relatorios.carregando is False
    assert get_redirects(eventos) == []

    assert [ponto["valor"] for ponto in relatorios.pontos_treinos][-2:] == [1, 1]
    assert relatorios.pontos_sono[0]["texto"] == "7,5 h"
    assert [ponto["texto"] for ponto in relatorios.pontos_peso] == ["72,4 kg", "71,8 kg"]
    assert relatorios.pontos_calorias[-2]["texto"] == "650 kcal"
    for relatorio in ("treinos", "sono", "peso", "calorias"):
        assert getattr(relatorios, f"suficiente_{relatorio}") is True
        assert getattr(relatorios, f"erro_{relatorio}") == ""


def test_usuario_sem_registros_fica_sem_dados_suficientes(estados, xano):
    relatorios, _ = estados
    respostas, _ = xano
    for nome in respostas:
        respostas[nome] = []

    run_start(relatorios)

    for relatorio in ("treinos", "sono", "peso", "calorias"):
        assert getattr(relatorios, f"suficiente_{relatorio}") is False
        assert getattr(relatorios, f"erro_{relatorio}") == ""
    # as semanas e os dias continuam existindo, só com 0 / sem valor
    assert len(relatorios.pontos_treinos) == 8
    assert all(ponto["valor"] is None for ponto in relatorios.pontos_calorias)


def test_falha_no_sono_nao_derruba_os_outros_cards(estados, xano):
    relatorios, _ = estados
    respostas, chamadas = xano
    respostas["list_sono"] = XanoError("indisponivel")

    run_start(relatorios)

    assert relatorios.erro_sono == MENSAGENS_FALHA["sono"]
    assert relatorios.pontos_sono == []
    assert relatorios.suficiente_sono is False
    assert len(chamadas) == 4
    assert relatorios.suficiente_treinos and relatorios.suficiente_peso and relatorios.suficiente_calorias
    assert relatorios.erro_treinos == relatorios.erro_peso == relatorios.erro_calorias == ""


def test_limite_de_requisicoes_pede_para_aguardar(estados, xano):
    relatorios, _ = estados
    respostas, _ = xano
    respostas["list_refeicoes"] = XanoError("limite_requisicoes")

    run_start(relatorios)

    assert relatorios.erro_calorias == MENSAGEM_LIMITE_REQUISICOES


def test_token_rejeitado_encerra_sessao_e_vai_para_login(estados, xano):
    relatorios, sessao = estados
    respostas, chamadas = xano
    respostas["list_treinos"] = XanoError("nao_autorizado")

    eventos = run_start(relatorios)

    assert sessao.token == ""
    assert get_redirects(eventos) == ["/login"]
    # não continua chamando o Xano com um token inválido
    assert len(chamadas) == 1


def test_sem_sessao_verificada_nao_chama_o_xano(estados, xano):
    relatorios, sessao = estados
    _, chamadas = xano
    sessao.sessao_verificada = False

    run_start(relatorios)

    assert chamadas == []


def test_tipo_padrao_e_escolha_valida_por_relatorio(estados):
    relatorios, _ = estados

    assert (relatorios.tipo_treinos, relatorios.tipo_sono, relatorios.tipo_peso, relatorios.tipo_calorias) == (
        "colunas",
        "colunas",
        "linhas",
        "colunas",
    )

    RelatoriosState.set_chart_type.fn(relatorios, "sono", "linhas")

    assert relatorios.grafico_sono == "linhas"
    assert relatorios.tipo_sono == "linhas"
    assert relatorios.tipo_treinos == "colunas"


def test_set_chart_type_recusa_relatorio_ou_tipo_invalido(estados):
    relatorios, _ = estados

    RelatoriosState.set_chart_type.fn(relatorios, "sono", "pizza")
    RelatoriosState.set_chart_type.fn(relatorios, "carregando", "linhas")
    RelatoriosState.set_chart_type.fn(relatorios, "../peso", "linhas")

    assert relatorios.grafico_sono == ""
    assert relatorios.carregando is True
    assert relatorios.grafico_peso == ""


def test_valor_invalido_salvo_no_navegador_cai_no_padrao(estados):
    relatorios, _ = estados
    relatorios.grafico_peso = "rosca"

    assert relatorios.tipo_peso == "linhas"
