# Design: Cadastro do perfil

## Objetivo

Implementar a primeira tela de onboarding do Pulse com base no schema do Xano para captar as informações de perfil do usuário.

## UI proposta

- Página responsiva com layout em cartão centralizado
- Seção de dados pessoais com nome, data de nascimento, sexo e altura
- Seção de objetivos e rotina com modalidade favorita, objetivo, horário de treino e meta semanal
- Checkbox para informar se o usuário deseja registrar medidas corporais
- Botão principal para salvar o perfil
- Área de mensagens de sucesso/erro

## Fluxo de interação

1. Usuário abre a página de cadastro.
2. Preenche os campos obrigatórios.
3. Clique em "Salvar perfil".
4. O estado valida os campos e envia o payload para o Xano quando configurado.
5. Exibe mensagem final de confirmação ou erro.

## Payload para o Xano

```python
payload = {
    "nome": self.nome,
    "data_de_nascimento": self.data_nascimento,
    "sexo": self.sexo,
    "altura_cm": float(self.altura_cm) if self.altura_cm else None,
    "tipo_fisico": float(self.tipo_fisico) if self.tipo_fisico else None,
    "nivel_fisico": self.nivel_fisico,
    "modalidade_fav": self.modalidade_fav,
    "horario_fav_de_treino": int(self.horario_fav_de_treino) if self.horario_fav_de_treino else None,
    "meta_semanal": int(self.meta_semanal) if self.meta_semanal else None,
    "objetivo": self.objetivo,
    "medidas": self.medidas,
    "data_atualizacao": datetime.now(timezone.utc).isoformat(),
}
```

## Observações de implementação

- A comunicação com o Xano deve usar `httpx` com `XANO_API_URL` e `XANO_API_KEY` quando disponíveis.
- Quando o backend não estiver configurado, o sistema mostra uma mensagem informando que o perfil foi validado e está pronto para envio.
- A página deve seguir a identidade visual do Pulse em um visual limpo e profissional.
