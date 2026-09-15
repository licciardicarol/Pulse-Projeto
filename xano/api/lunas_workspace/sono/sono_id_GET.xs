// Get Sono record
query "sono/{sono_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int sono_id? filters=min:1
  }

  stack {
    db.get Sono {
      field_name = "id"
      field_value = $input.sono_id
    } as $sono
  
    precondition ($sono != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $sono
  guid = "1vmGRI4iCBGs8JabmvlMcRmHNH8"
}