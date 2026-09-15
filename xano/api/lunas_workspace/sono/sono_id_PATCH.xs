// Edit Sono record
query "sono/{sono_id}" verb=PATCH {
  api_group = "Luna's Workspace"

  input {
    int sono_id? filters=min:1
    dblink {
      table = "Sono"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Sono {
      field_name = "id"
      field_value = $input.sono_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $sono
  }

  response = $sono
  guid = "DNn3Fx2DWWRLs97XXUNYFSdtyN0"
}