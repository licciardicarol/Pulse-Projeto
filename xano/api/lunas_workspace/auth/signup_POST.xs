// Signup and retrieve an authentication token
query "auth/signup" verb=POST {
  api_group = "Luna's Workspace"

  input {
    text nome filters=trim|min:1|max:50
    email email filters=lower|trim
  
    // mesma regra da tela de cadastro: mínimo de 8 caracteres
    password senha filters=min:8
  }

  stack {
    db.get user {
      field_name = "email"
      field_value = $input.email
    } as $user
  
    precondition ($user == null) {
      error_type = "accessdenied"
      error = "This account is already in use."
    }
  
    db.add user {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        nome      : $input.nome
        email     : $input.email
        senha     : $input.senha
      }
    } as $user
  
    // todo usuário nasce com um Perfil vinculado, em modo onboarding
    db.add Perfil {
      data = {
        created_at          : "now"
        user_id             : $user.id
        nome                : $input.nome
        medidas             : false
        onboarding_concluido: false
      }
    } as $perfil
  
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  }

  response = {authToken: $authToken}
  guid = "8SbmGdEx6sdXrb2I5qpD2J9tpGs"
}