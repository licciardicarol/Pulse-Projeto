// Add Profiles record
query profiles verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Perfil"
    }
  }

  stack {
    db.add Perfil {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $profiles
  }

  response = $profiles
  guid = "eFwPAAHsobpGkRrE-lrojmjtKAI"
}