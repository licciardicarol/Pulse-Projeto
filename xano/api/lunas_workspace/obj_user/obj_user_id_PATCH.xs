// Edit Obj_user record
query "obj_user/{obj_user_id}" verb=PATCH {
  api_group = "Luna's Workspace"

  input {
    int obj_user_id? filters=min:1
    dblink {
      table = "Obj_user"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Obj_user {
      field_name = "id"
      field_value = $input.obj_user_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $obj_user
  }

  response = $obj_user
  guid = "5KwV2ZqRvT9le1Xlj9DHk1UU_rM"
}