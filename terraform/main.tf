variable "project_id" {
  description = "Project ID to deploy to"
  type        = string
}
variable "region" {
  description = "Region to deploy to"
  type        = string
  default     = "europe-west2"
}
variable "docker_image" {
  description = "Docker image to deploy to Cloud Run"
  type        = string
}
variable "slack_bot_token" {
  description = "Slack App bot token"
  type        = string
}
variable "slack_channel" {
  description = "Slack channel to post the song to"
  type        = string
}
variable "slack_bot_signing_secret" {
  description = "Slack signing secret to verify the request is from Slack"
  type        = string
}
provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {
}

resource "google_storage_bucket" "tfstate" {
  name          = "tfstate_musical-chair-slackbot"
  force_destroy = true
  location      = var.region
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}

# To use the above bucket as a backend for terraform:
# 1. Apply this terraform file using `terraform apply` which will use a local state file
#    - The apply creates the bucket that will be used as a backend for terraform
# 2. Uncomment the following backend configuration and run `terraform init` which will see that the
#    state location has changed and will ask if you want to migrate the state to the new location.
#    Enter `yes` to migrate the state to the new location.

# terraform {
#   backend "gcs" {
#     bucket = "tfstate_musical-chair-slackbot"
#     prefix = "terraform/state"
#   }
# }

resource "google_secret_manager_secret" "slack_bot_token" {
  secret_id = "musical-chair-slack-bot-token"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "slack_bot_signing_secret" {
  secret_id = "musical-chair-slack-signing-secret"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "slack_bot_token_secret" {
  secret = google_secret_manager_secret.slack_bot_token.id
  secret_data = var.slack_bot_token
}

resource "google_secret_manager_secret_version" "slack_bot_signing_secret" {
  secret = google_secret_manager_secret.slack_bot_signing_secret.id
  secret_data = var.slack_bot_signing_secret
}

resource "google_secret_manager_secret_iam_member" "slack_bot_token_secret_access" {
  secret_id = google_secret_manager_secret.slack_bot_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "slack_bot_signing_secret_access" {
  secret_id = google_secret_manager_secret.slack_bot_signing_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

resource "google_cloud_run_v2_service" "musical_chair" {
  name     = "musical-chair-cr"
  location = var.region
  template {
    scaling {
      max_instance_count = 1
    }
    containers {
      image = var.docker_image
      env {
        name  = "SLACK_CHANNEL_ID"
        value = var.slack_channel
      }
      env {
        name = "SLACK_BOT_TOKEN"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.slack_bot_token.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "SLACK_SIGNING_SECRET"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.slack_bot_signing_secret.secret_id
            version = "latest"
          }
        }
      }

    }
  }
  depends_on = [google_secret_manager_secret_iam_member.slack_bot_token_secret_access,
  google_secret_manager_secret_iam_member.slack_bot_signing_secret_access]
}

resource "google_cloud_run_v2_service_iam_policy" "policy" {
  location    = var.region
  name        = google_cloud_run_v2_service.musical_chair.name
  policy_data = jsonencode({
    bindings = [
      {
        role    = "roles/run.invoker"
        members = ["allUsers"]
      },
    ]
  })
}

resource "google_firestore_document" "mydoc" {
  project     = var.project_id
  collection  = "musical-chair"
  document_id = "state"
  fields      = "{\"something\":{\"mapValue\":{\"fields\":{\"some_bogus_key\":{\"stringValue\":\"a_bogus_value\"}}}}}"
}

resource "google_cloud_scheduler_job" "musical_chair_job" {
  name     = "musical_chair_daily_question"
  schedule = "0 10 * * 1-5"
  time_zone = "Africa/Johannesburg"
  http_target {
    uri = "${google_cloud_run_v2_service.musical_chair.uri}/ask-for-song"
    http_method = "POST"
  }
}
