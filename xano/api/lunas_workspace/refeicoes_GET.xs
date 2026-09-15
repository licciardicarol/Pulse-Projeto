// Query all Refeicoes records
query refeicoes verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Refeicoes {
      return = {type: "list"}
    } as $refeicoes
  }

  response = $refeicoes
  guid = "atCZi98VukPFsbjJodeK28_ek24"
}