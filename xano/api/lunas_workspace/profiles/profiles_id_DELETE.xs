// Delete Profiles record.
query "profiles/{profiles_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int profiles_id? filters=min:1
  }

  stack {
    db.del Perfil {
      field_name = "id"
      field_value = $input.profiles_id
    }
  }

  response = null
  guid = "v__uNo8P0cwkN39NjAjvqlYS7Js"
}