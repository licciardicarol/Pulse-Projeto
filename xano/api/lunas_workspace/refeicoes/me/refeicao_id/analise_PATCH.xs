// Grava a análise nutricional por IA de uma refeição do usuário autenticado.
// Só o servidor do Pulse chama: exige o token do dono E a chave de serviço (PULSE_ANALISE_SECRET).
// Altera apenas calorias, macros e analise_ia; data, tipo, descrição e dono nunca mudam.
query "refeicoes/me/{refeicao_id}/analise" verb=PATCH {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int refeicao_id filters=min:1
    decimal calorias filters=min:0|max:5000
    decimal proteinas filters=min:0|max:500
    decimal carboidratos filters=min:0|max:500
    decimal gorduras filters=min:0|max:500
    text analise_ia filters=trim|min:1|max:300
    text chave_servico {
      sensitive = true
    }
  }

  stack {
    // chave de serviço primeiro: sem ela nada é consultado nem alterado
    precondition ($env.PULSE_ANALISE_SECRET != null && $env.PULSE_ANALISE_SECRET != "" && $input.chave_servico == $env.PULSE_ANALISE_SECRET) {
      error_type = "accessdenied"
      error = "Access denied."
    }
  
    db.get Refeicoes {
      field_name = "id"
      field_value = $input.refeicao_id
    } as $refeicao
  
    // refeição inexistente ou de outro usuário: mesma resposta, sem revelar que existe
    precondition ($refeicao != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    precondition ($refeicao.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    db.patch Refeicoes {
      field_name = "id"
      field_value = $input.refeicao_id
      data = {
        calorias    : $input.calorias
        proteinas   : $input.proteinas
        carboidratos: $input.carboidratos
        gorduras    : $input.gorduras
        analise_ia  : $input.analise_ia
      }
    } as $refeicao_atualizada
  }

  response = $refeicao_atualizada
  guid = "21SjJECltnAuhhP7zNCm2BpHcY8"
}