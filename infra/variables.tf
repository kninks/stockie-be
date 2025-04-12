variable "project_id" {}
variable "region" {
  default = "asia-southeast1"
}
variable "image_tag" {}

# Secrets (will be passed via TF_VAR_*)
variable "service_account_email" {}
variable "database_url" {}
variable "ml_server_url" {}
variable "discord_webhook_url" {}
variable "redis_host" {}
variable "redis_port" {}
variable "backend_api_key" {}
variable "client_api_key" {}
variable "ml_server_api_key" {}
variable "debug" {}
variable "log_level" {}
variable "allowed_origins" {}
