import json

from projetofacul.pages.treinos_page import SUBTITULO, TREINOS_PAGE_CSS, treinos_page, workout_item
from projetofacul.states.treinos_state import TreinosState

PAGINA = str(treinos_page())


def escapar(texto: str) -> str:
    # o Reflex serializa acentos como sequências \uXXXX ao converter componentes em texto
    return json.dumps(texto)[1:-1]


def test_cabecalho_e_estado_vazio():
    assert escapar("Treinos") in PAGINA
    assert SUBTITULO == "Registre suas sessões de treino e acompanhe seu histórico."
    assert escapar(SUBTITULO) in PAGINA
    assert escapar("Novo treino") in PAGINA
    assert escapar("Nenhum treino ainda") in PAGINA
    assert escapar('Toque em "Novo treino" para registrar sua primeira sessão.') in PAGINA
    assert "exercícios" not in SUBTITULO


def test_navbar_com_treinos_ativo_e_sem_social():
    assert '"aria-current":"page"' in PAGINA
    assert "Social" not in PAGINA


def test_carregando_e_erro_com_tentar_novamente():
    assert '"aria-busy":"true"' in PAGINA
    assert escapar("Carregando treinos") in PAGINA
    assert escapar("Tentar novamente") in PAGINA
    assert "start_page" in PAGINA


def test_css_responsivo_e_movimento_reduzido():
    assert "width: min(1200px, 100%)" in TREINOS_PAGE_CSS
    assert "@media (max-width: 640px)" in TREINOS_PAGE_CSS
    assert ".trn-header .trn-button { width: 100%; }" in TREINOS_PAGE_CSS
    assert "@media (prefers-reduced-motion: reduce)" in TREINOS_PAGE_CSS
    assert "min-height: 44px" in TREINOS_PAGE_CSS
    assert "transform: scale(.98)" in TREINOS_PAGE_CSS


def test_modal_com_campos_rotulos_e_placeholders():
    assert '"aria-labelledby":"trn-modal-titulo"' in PAGINA
    assert escapar("Novo treino") in PAGINA
    assert '"aria-label":"Fechar"' in PAGINA
    for campo in ("data", "duracao_minutos", "nome", "categoria", "intensidade", "observacoes"):
        assert f'htmlFor:"trn-{campo}"' in PAGINA
        assert f'id:"trn-{campo}"' in PAGINA
    for rotulo in ("Data", "Duração (min)", "Nome", "Categoria", "Intensidade", "Observações"):
        assert escapar(rotulo) in PAGINA
    for placeholder in ("Ex.: Peito e tríceps", "Musculação, corrida...", "Leve, moderada, alta"):
        assert escapar(placeholder) in PAGINA
    assert '"aria-live":"polite"' in PAGINA
    assert escapar("Salvar treino") in PAGINA


def test_limites_do_formulario_iguais_aos_da_validacao():
    assert "min:1" in PAGINA and "max:1440" in PAGINA
    for limite in (60, 40, 20, 500):
        assert f"maxLength:{limite}" in PAGINA


def test_sem_select_nem_opcoes_inventadas():
    # categoria e intensidade são texto livre no Xano
    assert "SelectTrigger" not in PAGINA
    for inexistente in ("Superior", "Inferior", "Full body"):
        assert inexistente not in PAGINA


def test_modal_responsivo():
    assert "min(560px" in TREINOS_PAGE_CSS
    assert ".trn-form-grid { grid-template-columns: minmax(0, 1fr); }" in TREINOS_PAGE_CSS
    assert ".trn-dialog { width: calc(100vw - 16px); max-height: calc(100dvh - 24px); }" in TREINOS_PAGE_CSS


def test_card_mostra_opcionais_so_quando_preenchidos():
    item = str(workout_item(TreinosState.treinos[0]))
    # cada opcional só é renderizado quando diferente de vazio
    for campo in ("categoria", "intensidade", "observacoes", "duracao"):
        assert f'["{campo}"]?.valueOf?.() === ""?.valueOf?.()' in item
    assert "trn-chip-intensity" in item


def test_lixeira_tem_rotulo_descritivo():
    item = str(workout_item(TreinosState.treinos[0]))
    assert "aria-label" in item
    assert "Excluir treino " in item
    assert "ask_delete" in item


def test_confirmacao_de_exclusao():
    assert escapar("Excluir este treino?") in PAGINA
    assert escapar("Cancelar") in PAGINA
    assert escapar("Excluir") in PAGINA
    assert "confirm_delete" in PAGINA


def test_microinteracoes_respeitam_movimento_reduzido():
    assert ".trn-item:hover { border-color: rgba(59,147,255,.35)" in TREINOS_PAGE_CSS
    assert "@keyframes trn-fade-in" in TREINOS_PAGE_CSS
    reduzido = TREINOS_PAGE_CSS.split("@media (prefers-reduced-motion: reduce)")[1]
    assert ".trn-item" in reduzido and ".trn-dialog" in reduzido
    assert "#FBBF24" in TREINOS_PAGE_CSS  # token `warning` do tema, sem cor avulsa


def test_foco_volta_ao_botao_novo_treino_ao_fechar():
    from projetofacul.pages.treinos_page import ID_BOTAO_NOVO_TREINO

    assert f'id:"{ID_BOTAO_NOVO_TREINO}"' in PAGINA
    # modal e confirmação de exclusão devolvem o foco ao botão
    assert PAGINA.count("onCloseAutoFocus") == 2
    assert f"document.getElementById('{ID_BOTAO_NOVO_TREINO}')?.focus()" in PAGINA
