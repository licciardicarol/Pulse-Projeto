// Query all Profiles records
query profiles verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Perfil {
      return = {type: "list"}
    } as $profiles
  }

  response = $profiles
  guid = "51KZlerc4O5oVl9UT9bUarjiK8g"
}