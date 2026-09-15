// Query all Sono records
query sono verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Sono {
      return = {type: "list"}
    } as $sono
  }

  response = $sono
  guid = "nsqfuFJ61rKhPZHbGBsYUz00XtM"
}