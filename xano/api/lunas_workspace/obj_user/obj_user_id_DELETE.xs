// Delete Obj_user record.
query "obj_user/{obj_user_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int obj_user_id? filters=min:1
  }

  stack {
    db.del Obj_user {
      field_name = "id"
      field_value = $input.obj_user_id
    }
  }

  response = null
  guid = "CxxVrUddvs0-S1SUwy4IbI4rXnU"
}