import json

from projetofacul.pages.refeicoes_page import REFEICOES_PAGE_CSS
from projetofacul.pages.sono_page import SONO_PAGE_CSS, empty_state, page_header, record_item, sono_page
from projetofacul.states.sono_state import SonoState

PAGINA = str(sono_page())


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \\uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


def test_cabecalho_e_textos_da_tela():
    assert escapar("Sono") in PAGINA
    assert escapar(
        "Registre início, fim e qualidade do sono. Esses dados alimentam as recomendações "
        "de recuperação e de intensidade de treino."
    ) in PAGINA
    assert "LucideMoon" in str(page_header())
    assert "LucideMoon" in str(empty_state())
    for texto in ("Início do sono", "Fim do sono", "Qualidade do sono", "Observações (opcional)",
                  "Acordou cansado? Sonhos, interrupções, cafeína à noite…", "Duração: ", "Salvar sono",
                  "Salvar alterações", "Cancelar edição", "Histórico", "Tentar novamente",
                  "Nenhum registro de sono ainda", "Preencha o horário de início e de fim do sono para começar.",
                  "Excluir registro de sono?"):
        assert escapar(texto) in PAGINA, texto
    assert escapar("em construção") not in PAGINA


def test_cinco_opcoes_de_qualidade_com_estado_acessivel():
    for numero, rotulo in ((1, "Muito ruim"), (2, "Ruim"), (3, "Regular"), (4, "Bom"), (5, "Muito bom")):
        assert escapar(f"Qualidade {numero} de 5: {rotulo}") in PAGINA
    assert PAGINA.count('"aria-pressed"') == 5
    assert '"aria-label":"Qualidade do sono, de 1 a 5"' in PAGINA


def test_campos_com_rotulo_e_erro_ligado():
    for campo in ("sono-inicio", "sono-fim", "sono-observacoes"):
        assert f'htmlFor:"{campo}"' in PAGINA
        assert f'id:"{campo}"' in PAGINA
        assert f'id:"{campo}-erro"' in PAGINA
    assert PAGINA.count('type:"datetime-local"') == 2
    assert '"aria-describedby":"sono-inicio-erro"' in PAGINA
    assert '"aria-describedby":"sono-qualidade-erro"' in PAGINA
    assert "maxLength:500" in PAGINA


def test_clicar_na_data_abre_calendario_e_hora():
    for campo in ("sono-inicio", "sono-fim"):
        assert f"document.getElementById('{campo}').showPicker()" in PAGINA
    assert escapar("Datas e horas no horário de Brasília. O dia vira à meia-noite (00:00).") in PAGINA


def test_botao_salvar_depende_da_validacao_e_do_envio():
    assert "pode_salvar" in PAGINA
    assert "save_sono" in PAGINA
    assert '"aria-busy"' in PAGINA


def test_item_tem_editar_e_excluir_com_rotulos():
    item = str(record_item(SonoState.registros[0]))
    assert escapar("Editar registro de sono de ") in item
    assert escapar("Excluir registro de sono de ") in item
    assert "start_edit" in item and "ask_delete" in item
    assert "ref-item" in item


def test_reusa_o_css_de_refeicoes():
    assert '"ref-page"' in PAGINA and '"ref-header-icon"' in PAGINA and '"ref-empty"' in PAGINA
    assert '"ref-skeleton"' in PAGINA and '"ref-button"' in PAGINA and '"ref-input"' in PAGINA
    assert REFEICOES_PAGE_CSS.strip()[:40] in PAGINA


def test_css_proprio_responsivo_sem_cores_novas():
    assert "@media (max-width: 640px)" in SONO_PAGE_CSS
    assert "@media (pointer: coarse)" in SONO_PAGE_CSS
    assert "min-height: 44px" in SONO_PAGE_CSS
    assert "__" not in SONO_PAGE_CSS  # todos os tokens foram aplicados
