import json

from projetofacul.pages.peso_page import PESO_PAGE_CSS, peso_page, weight_item
from projetofacul.states.peso_state import PesoState

PAGINA = str(peso_page())


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


def test_textos_da_pagina():
    for texto in (
        "Peso corporal",
        "Registre seu peso e acompanhe as variações.",
        "Nenhum peso registrado ainda",
        "Registre seu peso de hoje para começar a acompanhar sua evolução.",
        "Peso atual",
        "Desde o 1º registro",
        "Falta para a meta",
        "Disponível em breve",
        "Salvar registro",
        "Tentar novamente",
        "Excluir este registro?",
    ):
        assert escapar(texto) in PAGINA


def test_campos_com_label_e_peso_decimal():
    for campo in ("peso-data", "peso-horario", "peso-valor"):
        assert f'htmlFor:"{campo}"' in PAGINA
        assert f'id:"{campo}"' in PAGINA
    assert 'inputMode:"decimal"' in PAGINA
    assert 'type:"date"' in PAGINA and 'type:"time"' in PAGINA
    assert '"aria-live":"polite"' in PAGINA


def test_lixeira_tem_rotulo_descritivo():
    item = str(weight_item(PesoState.registros[0]))
    assert escapar("Excluir registro de ") in item


def test_css_responsivo_e_movimento_reduzido():
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in PESO_PAGE_CSS
    assert "@media (max-width: 640px)" in PESO_PAGE_CSS
    assert ".peso-summary-card:first-child { grid-column: 1 / -1; }" in PESO_PAGE_CSS
    assert ".peso-form-actions .peso-button { width: 100%; }" in PESO_PAGE_CSS
    assert "@media (prefers-reduced-motion: reduce)" in PESO_PAGE_CSS
    assert "min-height: 44px" in PESO_PAGE_CSS
    assert "width: min(1200px, 100%)" in PESO_PAGE_CSS
