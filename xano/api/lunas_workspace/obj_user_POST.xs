// Add Obj_user record
query obj_user verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Obj_user"
    }
  }

  stack {
    db.add Obj_user {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $obj_user
  }

  response = $obj_user
  guid = "kBFAa4BeL9NdDXGFYOMAl_Gd1vA"
}