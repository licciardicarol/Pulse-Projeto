// Add Sono record
query sono verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Sono"
    }
  }

  stack {
    db.add Sono {
      enforce_hidden_fields = false
      data = {
        created_at : "now"
        inicio_sono: null|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo"
        fim_sono   : ""|format_timestamp:"Y-m-d H:i:s":"America/Sao_Paulo"
      }
    } as $sono
  }

  response = $sono
  guid = "m4m5xU41G7FecgSSp1h1n1oe_iw"
}