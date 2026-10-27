// Registra uma refeição do usuário autenticado (RLS: dono sempre vem do token)
// inputs explícitos: sem user_id e sem valores nutricionais (preenchidos só pela IA no futuro)
query "refeicoes/me" verb=POST {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    date data_refeicao
    enum tipo {
      values = [
        "Café da manhã"
        "Almoço"
        "Café da tarde"
        "Jantar"
      ]
    }
  
    text descricao filters=trim|min:3|max:500
  }

  stack {
    // data da refeição não pode estar no futuro
    precondition (($input.data_refeicao|to_timestamp) <= ("now"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid meal date."
    }
  
    db.add Refeicoes {
      data = {
        created_at   : "now"
        user_id      : $auth.id
        data_refeicao: $input.data_refeicao
        tipo         : $input.tipo
        descricao    : $input.descricao
      }
    } as $refeicao
  }

  response = $refeicao
  guid = "rLA01rZ1-W9ej9VTIZH8vyKS2KM"
}