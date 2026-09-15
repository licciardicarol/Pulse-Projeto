// Get Profiles record
query "profiles/{profiles_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int profiles_id? filters=min:1
  }

  stack {
    db.get Perfil {
      field_name = "id"
      field_value = $input.profiles_id
    } as $profiles
  
    precondition ($profiles != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $profiles
  guid = "DsiFEonCka7h4vbNLKwy6r8oxe8"
}