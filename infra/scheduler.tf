resource "google_cloud_scheduler_job" "pull_trading_data" {
  name        = "pull-trading-data-job"
  description = "Trigger daily trading data pull"
  schedule    = "0 18 * * *" # 6 PM every day
  time_zone   = "Asia/Bangkok"

  http_target {
    http_method = "POST"
    uri         = "https://${var.backend_domain}/api/jobs/pull-trading-data"
    oidc_token {
      service_account_email = var.scheduler_service_account
    }
    headers = {
      "Content-Type" = "application/json"
      "X-API-Key"    = var.backend_api_key
    }
  }
}

resource "google_cloud_scheduler_job" "infer_and_save" {
  name        = "infer-and-save-job"
  description = "Run and save inference predictions"
  schedule    = "0 20 * * *" # 8 PM every day
  time_zone   = "Asia/Bangkok"

  http_target {
    http_method = "POST"
    uri         = "https://${var.backend_domain}/api/jobs/trigger-infer-and-save"
    oidc_token {
      service_account_email = var.scheduler_service_account
    }
    headers = {
      "Content-Type" = "application/json"
      "X-API-Key"    = var.backend_api_key
    }
  }
}

resource "google_cloud_scheduler_job" "rank_predictions" {
  name        = "rank-predictions-job"
  description = "Rank stock predictions"
  schedule    = "0 22 * * *" # 10 PM every day
  time_zone   = "Asia/Bangkok"

  http_target {
    http_method = "POST"
    uri         = "https://${var.backend_domain}/api/jobs/rank-predictions"
    oidc_token {
      service_account_email = var.scheduler_service_account
    }
    headers = {
      "Content-Type" = "application/json"
      "X-API-Key"    = var.backend_api_key
    }
  }
}

resource "google_cloud_scheduler_job" "evaluate_accuracy" {
  name        = "evaluate-accuracy-job"
  description = "Evaluate prediction accuracy"
  schedule    = "30 23 * * 6" # 11:30 PM every Saturday
  time_zone   = "Asia/Bangkok"

  http_target {
    http_method = "POST"
    uri         = "https://${var.backend_domain}/api/jobs/evaluate-accuracy"
    oidc_token {
      service_account_email = var.scheduler_service_account
    }
    headers = {
      "Content-Type" = "application/json"
      "X-API-Key"    = var.backend_api_key
    }
  }
}

resource "google_cloud_scheduler_job" "cleanup_old_data" {
  name        = "cleanup-old-data-job"
  description = "Clean up old data weekly"
  schedule    = "30 23 * * 6" # 11:30 PM every Saturday
  time_zone   = "Asia/Bangkok"

  http_target {
    http_method = "DELETE"
    uri         = "https://${var.backend_domain}/api/jobs/cleanup"
    oidc_token {
      service_account_email = var.scheduler_service_account
    }
    headers = {
      "Content-Type" = "application/json"
      "X-API-Key"    = var.backend_api_key
    }
  }
}
