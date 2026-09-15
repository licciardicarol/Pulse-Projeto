// Query all Obj_user records
query obj_user verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Obj_user {
      return = {type: "list"}
    } as $obj_user
  }

  response = $obj_user
  guid = "VyQE4ISQX2c-n8wXPNnRTrVbo0Y"
}