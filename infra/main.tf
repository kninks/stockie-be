provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_service" "stockie" {
  name     = "stockie-service"
  location = "asia-southeast1"

  template {
    spec {
      containers {
        image = "asia.gcr.io/${var.project_id}/stockie-service:${var.image_tag}"

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        env {
          name  = "ML_SERVER_URL"
          value = var.ml_server_url
        }
        env {
          name  = "DISCORD_WEBHOOK_URL"
          value = var.discord_webhook_url
        }
        env {
          name  = "REDIS_HOST"
          value = var.redis_host
        }
        env {
          name  = "REDIS_PORT"
          value = var.redis_port
        }
        env {
          name  = "BACKEND_API_KEY"
          value = var.backend_api_key
        }
        env {
          name  = "CLIENT_API_KEY"
          value = var.client_api_key
        }
        env {
          name  = "ML_SERVER_API_KEY"
          value = var.ml_server_api_key
        }
        env {
          name  = "DEBUG"
          value = var.debug
        }
        env {
          name  = "LOG_LEVEL"
          value = var.log_level
        }
        env {
          name  = "ALLOWED_ORIGINS"
          value = var.allowed_origins
        }
      }
    }
  }

  autogenerate_revision_name = true

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "invoker" {
  service  = google_cloud_run_service.stockie.name
  location = "asia-southeast1"
  role     = "roles/run.invoker"
  member   = "allUsers"
}