// Edit Profiles record
query "profiles/{profiles_id}" verb=PATCH {
  api_group = "Luna's Workspace"

  input {
    int profiles_id? filters=min:1
    dblink {
      table = "Perfil"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Perfil {
      field_name = "id"
      field_value = $input.profiles_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $profiles
  }

  response = $profiles
  guid = "0xs0HhmfvST3t9nueaJKE6JWi3A"
}