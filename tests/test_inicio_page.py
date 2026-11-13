import json

import projetofacul.projetofacul  # noqa: F401  registra as páginas e os States
from projetofacul.pages.inicio_page import (
    AVISO_IA,
    INICIO_PAGE_CSS,
    empty_content,
    error_content,
    inicio_page,
    preparing_content,
    ready_content,
    recommendation_card,
)

PAGINA = str(inicio_page())


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


def test_textos_do_card():
    assert escapar("Início") in PAGINA
    assert escapar("Sua recomendação de treino para hoje, a partir dos seus registros.") in PAGINA
    assert escapar("Recomendação de hoje") in PAGINA
    for rotulo in ("Recuperação", "Treino sugerido", "Alimentação", "/100", "Atualizar", "Atualizando…"):
        assert escapar(rotulo) in PAGINA, rotulo
    assert escapar("Preparando sua recomendação…") in PAGINA
    assert escapar("Comece registrando sua rotina") in PAGINA
    assert escapar(
        "Registre seu sono, suas refeições ou um treino para receber uma recomendação de treino "
        "feita a partir dos seus dados."
    ) in PAGINA
    assert escapar("Tentar novamente") in PAGINA


def test_sem_massa_magra_nem_area_em_construcao():
    assert "Massa magra" not in PAGINA and escapar("Massa magra") not in PAGINA
    assert escapar("Seu resumo do dia vai aparecer aqui.") not in PAGINA
    assert escapar("em construção") not in PAGINA


def test_aviso_de_ia_junto_da_recomendacao_uma_vez():
    assert AVISO_IA == (
        "Recomendação gerada por IA a partir dos seus registros. "
        "Não substitui a orientação de um profissional de saúde ou de educação física."
    )
    pronta = str(ready_content())
    assert pronta.count(escapar(AVISO_IA)) == 1
    assert PAGINA.count(escapar(AVISO_IA)) == 1


def test_recomendacao_mostra_os_campos_da_ia():
    pronta = str(ready_content())
    for campo in ("titulo", "texto", "recuperacao", "intensidade", "motivo_treino", "alimentacao"):
        assert f'["{campo}"]' in pronta, campo
    # rótulo acessível da recuperação e o número visual escondido do leitor de tela
    assert '["recuperacao_rotulo"]' in pronta
    assert "ini-sr-only" in pronta


def test_card_e_uma_secao_com_titulo():
    card = str(recommendation_card())
    assert '"aria-labelledby":"ini-card-titulo"' in card
    assert 'id:"ini-card-titulo"' in card
    assert '["gerada_em"]' in card


def test_estados_acessiveis():
    preparando = str(preparing_content())
    assert 'role:"status"' in preparando
    assert escapar("Preparando sua recomendação…") in preparando
    assert '"aria-busy":"true"' in preparando
    erro = str(error_content())
    assert '"aria-live":"polite"' in erro
    assert "start_page" in erro
    # falha do "Atualizar" também é anunciada
    assert '"aria-live":"polite"' in str(ready_content())


def test_botao_atualizar():
    card = str(recommendation_card())
    assert '"aria-label":"Atualizar recomenda\\u00e7\\u00e3o de hoje"' in card
    assert "refresh_recommendation" in card
    assert "atualizando" in card


def test_atalhos_para_registrar():
    vazio = str(empty_content())
    for texto, rota in (("Registrar sono", "/sono"), ("Registrar refeição", "/refeicoes"), ("Registrar treino", "/treinos")):
        assert escapar(texto) in vazio
        assert f'to:"{rota}"' in vazio


def test_css_responsivo_e_movimento_reduzido():
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in INICIO_PAGE_CSS
    responsivo = INICIO_PAGE_CSS.split("@media (max-width: 720px)")[1].split("}")[0]
    assert ".ini-boxes { grid-template-columns: minmax(0, 1fr)" in responsivo
    bloco_botao = INICIO_PAGE_CSS.split(".ini-refresh {")[1].split("}")[0]
    assert "min-height: 44px" in bloco_botao
    reduzido = INICIO_PAGE_CSS.split("@media (prefers-reduced-motion: reduce)")[1]
    assert ".ini-skeleton" in reduzido and ".ini-spinner" in reduzido
    # textos longos da IA quebram linha em vez de criar rolagem horizontal
    assert "overflow-wrap: anywhere" in INICIO_PAGE_CSS
