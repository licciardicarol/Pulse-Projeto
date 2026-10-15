// Salva o Perfil do usuário autenticado e conclui o onboarding (RLS: sempre por $auth.id)
query "perfil/me" verb=PATCH {
  api_group = "Luna's Workspace"
  auth = "user"

  // inputs explícitos: user_id, id e onboarding_concluido nunca vêm do cliente
  input {
    text nome filters=trim|min:1|max:50
    date data_de_nascimento
    enum sexo {
      values = ["Feminino", "Masculino", "Outro"]
    }

    decimal altura_cm filters=min:100|max:250
    enum tipo_fisico {
      values = ["Mesomorfo", "Ectomorfo", "Endomorfo"]
    }

    enum nivel_fisico {
      values = ["Iniciante", "Intermediário", "Avançado"]
    }

    enum[] modalidade_fav1 {
      values = [
        "Pilates"
        "Esportes de areia"
        "Yoga"
        "CrossFit"
        "Luta"
        "Funcional"
        "Cardio"
        "Musculação"
      ]
    }

    enum horario_fav_de_treino {
      values = ["Manhã", "Tarde", "Noite", "Madrugada"]
    }

    int meta_semanal filters=min:1|max:14
    enum objetivo {
      values = [
        "Hipertrofia (ganho de massa muscular)"
        "Emagrecimento (perda de gordura)"
        "Melhorar condicionamento físico"
        "Preservação de saúde mental"
      ]
    }

    bool medidas
  }

  stack {
    // pelo menos uma modalidade (o banco aceita lista vazia por causa do signup)
    precondition (($input.modalidade_fav1|count) > 0) {
      error_type = "inputerror"
      error = "Select at least one modality."
    }

    // data de nascimento no passado e não anterior a 1900
    precondition (($input.data_de_nascimento|to_timestamp) < ("now"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid birth date."
    }

    precondition (($input.data_de_nascimento|to_timestamp) >= ("1900-01-01"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid birth date."
    }

    db.get Perfil {
      field_name = "user_id"
      field_value = $auth.id
    } as $perfil

    precondition ($perfil != null) {
      error_type = "notfound"
      error = "Not Found."
    }

    db.patch Perfil {
      field_name = "id"
      field_value = $perfil.id
      data = {
        nome                 : $input.nome
        data_de_nascimento   : $input.data_de_nascimento
        sexo                 : $input.sexo
        altura_cm            : $input.altura_cm
        tipo_fisico          : $input.tipo_fisico
        nivel_fisico         : $input.nivel_fisico
        modalidade_fav1      : $input.modalidade_fav1
        horario_fav_de_treino: $input.horario_fav_de_treino
        meta_semanal         : $input.meta_semanal
        objetivo             : $input.objetivo
        medidas              : $input.medidas
        data_atualizacao     : "now"
        onboarding_concluido : true
      }
    } as $perfil_atualizado
  }

  response = $perfil_atualizado
}
