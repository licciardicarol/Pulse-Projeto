// Login and retrieve an authentication token
query "auth/login" verb=POST {
  api_group = "Luna's Workspace"

  input {
    email email filters=trim|lower
    text senha
  }

  stack {
    // nomes dos campos precisam bater com a tabela user (nome/senha)
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id", "senha"]
    } as $user
  
    // mesma mensagem para e-mail inexistente e senha errada
    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    security.check_password {
      text_password = $input.senha
      hash_password = $user.senha
    } as $pass_result
  
    precondition ($pass_result) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  }

  response = {authToken: $authToken}
  guid = "ecAMnXLuJooFFWiIYI5-y4tn16k"
}