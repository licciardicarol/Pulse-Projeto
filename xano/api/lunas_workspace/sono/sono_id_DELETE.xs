// Delete Sono record.
query "sono/{sono_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int sono_id? filters=min:1
  }

  stack {
    db.del Sono {
      field_name = "id"
      field_value = $input.sono_id
    }
  }

  response = null
  guid = "4P59fdVahSPk1_4d3wJ90zrfjFc"
}