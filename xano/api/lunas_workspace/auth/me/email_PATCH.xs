// Altera o e-mail do usuário autenticado, exigindo a senha atual
query "auth/me/email" verb=PATCH {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    email email filters=trim|lower
    text senha_atual
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "senha"]
    } as $user
  
    security.check_password {
      text_password = $input.senha_atual
      hash_password = $user.senha
    } as $senha_ok
  
    precondition ($senha_ok) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    // mensagem genérica: não confirma que o e-mail pertence a outra conta
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $email_em_uso
  
    precondition ($email_em_uso == null) {
      error_type = "badrequest"
      error = "Unable to update email."
    }
  
    db.patch user {
      field_name = "id"
      field_value = $auth.id
      data = {email: $input.email}
    } as $atualizado
  }

  response = {email: $input.email}
  guid = "eGm9QUeGBDcPiQ1pDxwpO72psLo"
}