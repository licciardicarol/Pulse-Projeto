// Get Obj_user record
query "obj_user/{obj_user_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int obj_user_id? filters=min:1
  }

  stack {
    db.get Obj_user {
      field_name = "id"
      field_value = $input.obj_user_id
    } as $obj_user
  
    precondition ($obj_user != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $obj_user
  guid = "17pr-f8qXugCTNG6RKAkSVzAS-0"
}