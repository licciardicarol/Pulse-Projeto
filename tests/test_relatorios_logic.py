from datetime import date, datetime, timedelta, timezone

import pytest

from projetofacul.logic.relatorios import (
    build_daily_calories,
    build_sleep_hours,
    build_weekly_workouts,
    build_weight_evolution,
    has_enough_data,
    normalize_chart_type,
)

# quarta-feira, como no cenário da spec
HOJE = date(2026, 11, 4)
BRASILIA = timezone(timedelta(hours=-3))


def ms(ano, mes, dia, hora=0, minuto=0) -> int:
    """Instante em horário de Brasília -> milissegundos UTC, como o Xano devolve."""
    return int(datetime(ano, mes, dia, hora, minuto, tzinfo=BRASILIA).timestamp() * 1000)


def noite(dia_inicio: date, duracao_minutos: int | None = None, hora_inicio: int = 23) -> dict:
    inicio = datetime(dia_inicio.year, dia_inicio.month, dia_inicio.day, hora_inicio, tzinfo=BRASILIA)
    fim = inicio + timedelta(minutes=duracao_minutos or 480)
    return {
        "inicio_sono": int(inicio.timestamp() * 1000),
        "fim_sono": int(fim.timestamp() * 1000),
        "duracao_minutos": duracao_minutos,
    }


# Frequência de treinos


def test_semanas_de_segunda_a_domingo_com_cenario_da_spec():
    treinos = [{"data": "2026-11-02"}, {"data": "2026-11-02"}, {"data": "2026-10-28"}]

    pontos = build_weekly_workouts(treinos, HOJE)

    assert [ponto["rotulo"] for ponto in pontos] == [
        "14/09", "21/09", "28/09", "05/10", "12/10", "19/10", "26/10", "02/11",
    ]
    assert [ponto["valor"] for ponto in pontos] == [0, 0, 0, 0, 0, 0, 1, 2]
    assert pontos[-1]["texto"] == "2 treinos"
    assert pontos[-2]["texto"] == "1 treino"
    assert has_enough_data("treinos", pontos)


def test_domingo_pertence_a_semana_que_comecou_na_segunda():
    pontos = build_weekly_workouts([{"data": "2026-11-01"}], HOJE)

    assert pontos[-2]["rotulo"] == "26/10"
    assert pontos[-2]["valor"] == 1


def test_treino_fora_da_janela_futuro_ou_sem_data_nao_conta():
    treinos = [
        {"data": "2026-08-04"},  # 3 meses atrás
        {"data": "2026-09-13"},  # domingo antes da primeira semana
        {"data": "2026-11-05"},  # amanhã
        {"data": None},
        {"data": "data inválida"},
    ]

    pontos = build_weekly_workouts(treinos, HOJE)

    assert all(ponto["valor"] == 0 for ponto in pontos)
    assert not has_enough_data("treinos", pontos)


# Horas de sono


def test_sono_limita_aos_30_mais_recentes_em_ordem_cronologica():
    registros = [noite(date(2026, 9, 1) + timedelta(days=i), 420 + i) for i in range(45)]

    pontos = build_sleep_hours(registros)

    assert len(pontos) == 30
    # a noite mais antiga mostrada é a 16ª (índice 15); a mais nova, a 45ª
    assert pontos[0]["valor"] == round((420 + 15) / 60, 1)
    assert pontos[-1]["valor"] == round((420 + 44) / 60, 1)
    assert pontos[-1]["rotulo"] == "16/10"


def test_sono_converte_minutos_em_horas_formatadas():
    pontos = build_sleep_hours([noite(date(2026, 11, 3), 450)])

    assert pontos == [{"rotulo": "04/11", "valor": 7.5, "texto": "7,5 h"}]


def test_sono_usa_inicio_e_fim_quando_falta_duracao_do_servidor():
    registro = noite(date(2026, 11, 3), 480)
    registro["duracao_minutos"] = None

    pontos = build_sleep_hours([registro])

    assert pontos[0]["valor"] == 8.0
    assert pontos[0]["texto"] == "8,0 h"


def test_sono_sem_duracao_valida_nao_aparece():
    sem_periodo = {"inicio_sono": None, "fim_sono": None, "duracao_minutos": None}
    fim_antes_do_inicio = {"inicio_sono": ms(2026, 11, 4, 7), "fim_sono": ms(2026, 11, 3, 23), "duracao_minutos": 0}

    pontos = build_sleep_hours([sem_periodo, fim_antes_do_inicio])

    assert pontos == []
    assert not has_enough_data("sono", pontos)


# Evolução do peso


def test_peso_em_ordem_cronologica_com_cenario_da_spec():
    registros = [
        {"peso": 71.8, "data_horario": ms(2026, 11, 1, 8), "created_at": 2},
        {"peso": 72.4, "data_horario": ms(2026, 10, 1, 8), "created_at": 1},
    ]

    pontos = build_weight_evolution(registros)

    assert pontos == [
        {"rotulo": "01/10", "valor": 72.4, "texto": "72,4 kg"},
        {"rotulo": "01/11", "valor": 71.8, "texto": "71,8 kg"},
    ]
    assert has_enough_data("peso", pontos)


def test_peso_invalido_e_descartado_e_um_registro_nao_basta():
    registros = [
        {"peso": "abc", "data_horario": ms(2026, 10, 1)},
        {"peso": None, "data_horario": ms(2026, 10, 2)},
        {"peso": 70, "data_horario": None},
        {"peso": 70.25, "data_horario": ms(2026, 10, 3)},
    ]

    pontos = build_weight_evolution(registros)

    assert pontos == [{"rotulo": "03/10", "valor": 70.25, "texto": "70,25 kg"}]
    assert not has_enough_data("peso", pontos)


def test_peso_usa_horario_de_brasilia_no_rotulo():
    # 01/11 01:00 UTC ainda é 31/10 em Brasília
    registro = {"peso": 70, "data_horario": ms(2026, 10, 31, 22)}

    assert build_weight_evolution([registro])[0]["rotulo"] == "31/10"


# Calorias


def refeicao(data: str, calorias: float, analisada: bool = True) -> dict:
    return {"data_refeicao": data, "calorias": calorias, "analise_ia": "ok" if analisada else ""}


def test_calorias_cobrem_14_dias_e_somam_so_refeicoes_analisadas():
    refeicoes = [
        refeicao("2026-11-03", 650),
        refeicao("2026-11-03", 900, analisada=False),
        refeicao("2026-11-04", 1200.4),
        refeicao("2026-11-04", 650),
    ]

    pontos = build_daily_calories(refeicoes, HOJE)

    assert len(pontos) == 14
    assert pontos[0]["rotulo"] == "22/10"
    assert pontos[-1] == {"rotulo": "04/11", "valor": 1850, "texto": "1.850 kcal"}
    assert pontos[-2] == {"rotulo": "03/11", "valor": 650, "texto": "650 kcal"}
    assert has_enough_data("calorias", pontos)


def test_dia_sem_refeicao_analisada_fica_sem_valor_e_nao_zero():
    pontos = build_daily_calories([refeicao("2026-11-02", 0, analisada=False)], HOJE)

    dia = next(ponto for ponto in pontos if ponto["rotulo"] == "02/11")
    assert dia["valor"] is None
    assert dia["texto"] == "—"
    assert not has_enough_data("calorias", pontos)


def test_refeicao_fora_dos_14_dias_ou_futura_nao_conta():
    pontos = build_daily_calories(
        [refeicao("2026-10-21", 500), refeicao("2026-11-05", 500), refeicao("", 500)], HOJE
    )

    assert all(ponto["valor"] is None for ponto in pontos)


# Tipo de gráfico


@pytest.mark.parametrize(
    ("valor", "relatorio", "esperado"),
    [
        ("linhas", "treinos", "linhas"),
        ("colunas", "peso", "colunas"),
        ("", "treinos", "colunas"),
        ("", "sono", "colunas"),
        ("", "calorias", "colunas"),
        ("", "peso", "linhas"),
        ("pizza", "sono", "colunas"),
        ("rosca", "peso", "linhas"),
    ],
)
def test_tipo_de_grafico_invalido_volta_ao_padrao(valor, relatorio, esperado):
    assert normalize_chart_type(valor, relatorio) == esperado
