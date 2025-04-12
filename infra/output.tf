output "cloud_run_url" {
  value = google_cloud_run_service.stockie.status[0].url
}

output "deployed_image" {
  value = "asia.gcr.io/${var.project_id}/stockie-service:${var.image_tag}"
}