variable "url" {
  type        = string
  description = "The URL used for the database"
}

env "local" {
  schema {
    src = "file://src/schema.sql"
  }
  url = var.url
  dev = "docker://postgres/18/dev?search_path=public"
}

lint {
  data_depend {
    error = true
  }
  incompatible {
    error = true
  }
  naming {
    error   = true
    match   = "^[a-z_]+$"
    message = "must be lowercase"
  }
}