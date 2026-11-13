// Devolve a recomendação mais recente do usuário autenticado para um dia (RLS: sempre por $auth.id).
// Sem recomendação nesse dia, a resposta é null: o app então gera uma nova.
query "recomendacoes/me/hoje" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    date data_recomendacao
  }

  stack {
    db.query Recomendacoes {
      where = $db.Recomendacoes.user_id == $auth.id && $db.Recomendacoes.data_recomendacao == $input.data_recomendacao
      sort = {created_at: "desc"}
      return = {type: "single"}
    } as $recomendacao
  }

  response = $recomendacao
  guid = "wyZ-S8HS0HjaqPjL__folD0iCYI"
}