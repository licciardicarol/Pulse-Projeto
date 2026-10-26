import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from projetofacul.logic.treinos import (
    build_treino_payload,
    build_workout_view,
    format_date_br,
    get_today_sao_paulo,
    sort_treinos,
    validate_treino,
)

HOJE = date(2026, 10, 26)
RAIZ = Path(__file__).resolve().parent.parent


def dados(**alteracoes):
    return {"data": "2026-10-26", "duracao_minutos": "60", "nome": "Peito e tríceps", "categoria": "",
            "intensidade": "", "observacoes": "", **alteracoes}


def test_campos_enviados_existem_na_tabela_do_xano():
    conteudo = (RAIZ / "xano" / "table" / "treinos.xs").read_text(encoding="utf-8")
    campos = set(re.findall(r"^\s*(?:text|int|date\?|date)\s+(\w+)\??", conteudo, re.MULTILINE))
    payload = build_treino_payload(dados(categoria="Musculação", intensidade="Alta", observacoes="ok"))
    assert set(payload) <= campos


def test_hoje_em_sao_paulo_as_22h():
    # 22h de 26/10 em São Paulo = 01h de 27/10 em UTC
    assert get_today_sao_paulo(datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)) == date(2026, 10, 26)
    assert get_today_sao_paulo(datetime(2026, 10, 27, 3, 0, tzinfo=timezone.utc)) == date(2026, 10, 27)


def test_hoje_independe_do_fuso_recebido():
    agora_toquio = datetime(2026, 10, 27, 10, 0, tzinfo=timezone(timedelta(hours=9)))
    assert get_today_sao_paulo(agora_toquio) == date(2026, 10, 26)
    assert get_today_sao_paulo(datetime(2026, 10, 27, 1, 0)) == date(2026, 10, 26)


def test_treino_valido_nao_tem_erros():
    assert validate_treino(dados(), HOJE) == {}
    assert validate_treino(dados(duracao_minutos="1", nome="ab"), HOJE) == {}
    assert validate_treino(dados(duracao_minutos="1440", nome="x" * 60), HOJE) == {}
    assert validate_treino(dados(categoria="x" * 40, intensidade="x" * 20, observacoes="x" * 500), HOJE) == {}
    assert validate_treino(dados(data="2025-01-01"), HOJE) == {}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [("duracao_minutos", "0"), ("duracao_minutos", "1441"), ("duracao_minutos", "60.5"),
     ("duracao_minutos", "-5"), ("duracao_minutos", ""), ("duracao_minutos", "abc"),
     ("nome", ""), ("nome", "a"), ("nome", "   a   "), ("nome", "x" * 61),
     ("categoria", "x" * 41), ("intensidade", "x" * 21), ("observacoes", "x" * 501),
     ("data", ""), ("data", "26/10/2026"), ("data", "2026-10-27")],
)
def test_treino_invalido_aponta_o_campo(campo, valor):
    assert set(validate_treino(dados(**{campo: valor}), HOJE)) == {campo}


def test_data_futura_compara_so_o_dia():
    # 23h59 em SP: o dia de hoje ainda é aceito, o de amanhã não
    hoje = get_today_sao_paulo(datetime(2026, 10, 27, 2, 59, tzinfo=timezone.utc))
    assert validate_treino(dados(data="2026-10-26"), hoje) == {}
    assert validate_treino(dados(data="2026-10-27"), hoje) == {"data": "A data não pode estar no futuro."}


def test_payload_so_com_campos_da_tela():
    assert build_treino_payload(dados(nome="  Perna  ")) == {
        "data": "2026-10-26",
        "duracao_minutos": 60,
        "nome": "Perna",
    }
    completo = build_treino_payload(dados(categoria=" Corrida ", intensidade="Leve", observacoes="5 km"))
    assert completo == {"data": "2026-10-26", "duracao_minutos": 60, "nome": "Peito e tríceps",
                        "categoria": "Corrida", "intensidade": "Leve", "observacoes": "5 km"}
    assert not {"user_id", "tipo", "inicio", "fim", "carga", "repeticoes"} & set(completo)


def test_ordem_mais_recentes_primeiro():
    treinos = [
        {"id": 1, "data": "2026-10-25"},
        {"id": 2, "data": "2026-10-26"},
        {"id": 3, "data": "2026-10-26"},
        {"id": 4, "data": "2026-10-24"},
    ]
    assert [treino["id"] for treino in sort_treinos(treinos)] == [3, 2, 1, 4]


def test_data_em_formato_brasileiro():
    assert format_date_br("2026-10-26") == "26/10/2026"
    assert format_date_br("") == ""


def test_card_sem_opcionais_nao_inventa_valores():
    vista = build_workout_view({"id": 7, "data": "2026-10-26", "duracao_minutos": 60, "nome": "Perna",
                                "categoria": None, "intensidade": "", "observacoes": None})
    assert vista == {"id": "7", "nome": "Perna", "data": "26/10/2026", "duracao": "60 min",
                     "categoria": "", "intensidade": "", "observacoes": ""}
