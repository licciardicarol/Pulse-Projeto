import json

from projetofacul.components.app_shell import APP_SHELL_CSS
from projetofacul.pages.refeicoes_page import REFEICOES_PAGE_CSS, meal_item, refeicoes_page
from projetofacul.states.refeicoes_state import RefeicoesState

PAGINA = str(refeicoes_page())


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


def test_textos_da_pagina_sem_promessa_de_ia_pronta():
    assert escapar("Refeições") in PAGINA
    assert escapar("Descreva o que você comeu. Em breve a IA estimará calorias e macronutrientes automaticamente.") in PAGINA
    assert escapar("Nova refeição") in PAGINA
    assert escapar("Nenhuma refeição registrada") in PAGINA
    assert escapar("Descreva sua primeira refeição para começar o seu histórico.") in PAGINA
    assert escapar("Aguardando análise") in PAGINA
    assert escapar("Tentar novamente") in PAGINA
    for rotulo in ("Calorias hoje", "Proteínas", "Carboidratos", "Gorduras"):
        assert escapar(rotulo) in PAGINA


def test_tipo_tem_exatamente_as_4_opcoes_do_xano():
    for opcao in ("Café da manhã", "Almoço", "Café da tarde", "Jantar"):
        assert f'value:"{escapar(opcao)}"' in PAGINA
    for inexistente in ("Lanche", "Pré-treino", "Pós-treino"):
        assert escapar(inexistente) not in PAGINA


def test_modal_e_campos_acessiveis():
    assert '"aria-labelledby":"ref-modal-titulo"' in PAGINA
    assert '"aria-label":"Fechar"' in PAGINA
    for campo in ("ref-data", "ref-tipo", "ref-descricao"):
        assert f'htmlFor:"{campo}"' in PAGINA
        assert f'id:"{campo}"' in PAGINA
    assert '"aria-live":"polite"' in PAGINA
    assert escapar("Excluir esta refeição?") in PAGINA
    assert escapar("Salvar") in PAGINA


def test_lixeira_tem_rotulo_descritivo():
    item = str(meal_item(RefeicoesState.refeicoes[0]))
    assert "aria-label" in item
    assert escapar("Excluir refeição: ") in item


def test_css_responsivo_e_movimento_reduzido():
    assert "grid-template-columns: repeat(4, minmax(0, 1fr))" in REFEICOES_PAGE_CSS
    assert "@media (max-width: 900px)" in REFEICOES_PAGE_CSS
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in REFEICOES_PAGE_CSS
    assert "@media (prefers-reduced-motion: reduce)" in REFEICOES_PAGE_CSS
    assert "min-height: 44px" in REFEICOES_PAGE_CSS
    assert "min(560px" in REFEICOES_PAGE_CSS


def test_erro_da_sessao_oferece_tentar_novamente():
    assert "retry_session" in PAGINA
    assert escapar("Recarrega a página e busca seus dados de novo") in PAGINA
    assert ".app-status-retry" in APP_SHELL_CSS


def test_destaque_do_radix_usa_azul_do_projeto():
    assert "--accent-9: #2B8CFF" in APP_SHELL_CSS
    assert "teal" not in APP_SHELL_CSS.lower()
