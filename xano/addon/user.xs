addon user {
  input {
    int user_id? {
      table = ""
    }
  }

  stack {
    db.query "" {
      where = $db.user.id == $input.user_id
      return = {type: "single"}
    }
  }

  guid = "X3-Wchj1L8gi0Wigs7SjhmkndFo"
}