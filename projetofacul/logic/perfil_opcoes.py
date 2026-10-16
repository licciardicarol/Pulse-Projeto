"""Opções do Perfil, espelhando os enums de `xano/table/perfil.xs`.

UI, validação e testes usam estas tuplas; o teste que lê o `.xs` garante que
nada diverge do Xano.
"""

OPCOES_SEXO = ("Feminino", "Masculino", "Outro")

# (valor, descrição) na ordem exibida na tela
OPCOES_BIOTIPO = (
    (
        "Ectomorfo",
        "Estrutura magra, dificuldade em ganhar peso e massa. Pulso e tornozelos finos, metabolismo acelerado.",
    ),
    (
        "Mesomorfo",
        "Estrutura atlética, ganha músculo com facilidade. Ombros largos, cintura estreita.",
    ),
    (
        "Endomorfo",
        "Estrutura mais robusta, tendência a acumular gordura. Ganho de massa mais fácil que perda.",
    ),
)
VALORES_BIOTIPO = tuple(valor for valor, _ in OPCOES_BIOTIPO)

OPCOES_CONDICIONAMENTO = ("Sedentário", "Iniciante", "Intermediário", "Avançado", "Atleta")

OPCOES_HORARIO = ("Manhã", "Tarde", "Noite", "Madrugada")

OPCOES_OBJETIVO = ("Perder gordura", "Ganhar massa", "Manter", "Performance")

OPCOES_MODALIDADES = (
    "Musculação",
    "Corrida",
    "Ciclismo",
    "Funcional",
    "Crossfit",
    "Luta",
    "Yoga",
    "Natação",
    "Esportes coletivos",
)
