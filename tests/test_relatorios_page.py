import json

from projetofacul.pages.relatorios_page import (
    CARDS_RELATORIO,
    MENSAGEM_SEM_DADOS,
    NOTAS_CALORIAS,
    RELATORIOS_PAGE_CSS,
    TIPOS_GRAFICO_UI,
    chart_type_selector,
    relatorios_page,
    report_card,
)
from projetofacul.states.relatorios_state import RelatoriosState


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


PAGINA = str(relatorios_page())


def test_quatro_cards_com_titulos_na_ordem_da_spec():
    titulos = [
        "Frequência de treinos (últimas 8 semanas)",
        "Horas de sono (últimos 30 registros)",
        "Evolução do peso",
        "Calorias ingeridas x gastas (últimos 14 dias)",
    ]

    assert [titulo for _, titulo, _ in CARDS_RELATORIO] == titulos
    posicoes = [PAGINA.index(escapar(titulo)) for titulo in titulos]
    assert posicoes == sorted(posicoes)
    assert PAGINA.count('className:"rel-card"') == 4
    assert escapar("Relatórios") in PAGINA


def test_seletor_so_tem_colunas_e_linhas_com_aria_pressed():
    assert [rotulo for _, rotulo, _ in TIPOS_GRAFICO_UI] == ["Colunas", "Linhas"]
    for ausente in ("Pizza", "Rosca", "PieChart"):
        assert ausente not in PAGINA

    seletor = str(chart_type_selector("sono", "Horas de sono", RelatoriosState.tipo_sono))
    assert seletor.count('"aria-pressed"') == 2
    assert 'role:"group"' in seletor or '"role":"group"' in seletor
    assert "set_chart_type" in seletor


def test_cada_card_tem_estado_vazio_tabela_e_ambos_os_graficos():
    for relatorio, titulo, periodo in CARDS_RELATORIO:
        card = str(report_card(relatorio, titulo, periodo))
        assert escapar(MENSAGEM_SEM_DADOS) in card
        assert f'id:"rel-{relatorio}-tabela"' in card
        assert 'className:"sr-only"' in card
        assert "BarChart" in card and "LineChart" in card
        assert f"pontos_{relatorio}" in card
        assert f"tipo_{relatorio}" in card
        assert "Tentar novamente" in card


def test_graficos_sem_animacao_com_lacunas_e_texto_formatado_no_tooltip():
    card = str(report_card("calorias", "Calorias", "Dia"))

    assert "isAnimationActive:false" in card
    assert "connectNulls:false" in card
    assert "item.payload.texto" in card
    assert "toLocaleString('pt-BR')" in card


def test_peso_em_linhas_acompanha_a_faixa_dos_dados_e_colunas_comecam_em_zero():
    peso = str(report_card("peso", "Evolução do peso", "Data"))
    sono = str(report_card("sono", "Horas de sono", "Noite"))

    assert '"dataMin - 1"' in peso
    assert "[0, \"auto\"]" in peso or '[0,"auto"]' in peso
    assert '"dataMin - 1"' not in sono


def test_card_de_calorias_avisa_sobre_ia_e_calorias_gastas():
    calorias = str(report_card("calorias", "Calorias", "Dia"))
    treinos = str(report_card("treinos", "Treinos", "Semana"))

    for nota in NOTAS_CALORIAS:
        assert escapar(nota) in calorias
        assert escapar(nota) not in treinos
    assert escapar("não substituem orientação") in calorias


def test_css_espaco_entre_cards_toque_responsivo_e_movimento_reduzido():
    assert "gap: 32px" in RELATORIOS_PAGE_CSS
    assert "min-height: 44px" in RELATORIOS_PAGE_CSS
    assert "@media (max-width: 520px)" in RELATORIOS_PAGE_CSS
    assert "prefers-reduced-motion" in RELATORIOS_PAGE_CSS
    assert ".sr-only" in RELATORIOS_PAGE_CSS
    assert "__" not in RELATORIOS_PAGE_CSS
