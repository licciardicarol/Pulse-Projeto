// Registra um peso do usuário autenticado (RLS: dono sempre vem do token)
// inputs explícitos: sem user_id
query "registro_peso/me" verb=POST {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    decimal peso
    timestamp data_horario
  }

  stack {
    // faixa plausível, dentro de decimal(5,2)
    precondition ($input.peso >= 20 && $input.peso <= 400) {
      error_type = "inputerror"
      error = "Invalid weight."
    }
  
    // no máximo 2 casas decimais
    precondition (($input.peso|round:2) == $input.peso) {
      error_type = "inputerror"
      error = "Invalid weight."
    }
  
    // a pesagem não pode estar no futuro
    precondition ($input.data_horario <= ("now"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid date."
    }
  
    db.add registro_Peso {
      data = {
        created_at  : "now"
        user_id     : $auth.id
        peso        : $input.peso
        data_horario: $input.data_horario
      }
    } as $registro
  }

  response = $registro
  guid = "yUoXdo6CVxmcr0oM6vu1xwv3Bq0"
}