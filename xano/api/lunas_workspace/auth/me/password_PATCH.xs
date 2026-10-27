// Altera a senha do usuário autenticado, exigindo a senha atual
// nunca devolve hash ou senha
query "auth/me/password" verb=PATCH {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    text senha_atual
  
    // mesma regra do signup e da tela de cadastro
    password nova_senha filters=min:8
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
  
    db.patch user {
      field_name = "id"
      field_value = $auth.id
      data = {senha: $input.nova_senha}
    } as $atualizado
  }

  response = {sucesso: true}
  guid = "fNwGNVhhmLwcd3SYaVZvce_niLE"
}