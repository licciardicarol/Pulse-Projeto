// Get the record belonging to the authentication token
query "auth/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "created_at", "nome", "email"]
    } as $user
  }

  response = $user
  guid = "ZXQ2Ajf_5kLv9PH7ciKVOCQME98"
}