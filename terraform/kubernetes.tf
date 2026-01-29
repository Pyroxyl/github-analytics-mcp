# Namespace
resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace_name

    labels = {
      app     = "github-analytics"
      managed = "terraform"
    }
  }
}

# Secret for GitHub token
resource "kubernetes_secret" "github_token" {
  metadata {
    name      = "github-analytics-secret"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    GITHUB_TOKEN = var.github_token
  }

  type = "Opaque"
}

# Deployment
resource "kubernetes_deployment" "api_gateway" {
  metadata {
    name      = "api-gateway"
    namespace = kubernetes_namespace.app.metadata[0].name

    labels = {
      app     = "api-gateway"
      managed = "terraform"
    }
  }

  spec {
    replicas = var.api_replicas

    selector {
      match_labels = {
        app = "api-gateway"
      }
    }

    template {
      metadata {
        labels = {
          app = "api-gateway"
        }
      }

      spec {
        container {
          name  = "api-gateway"
          image = "${var.image_name}:${var.image_tag}"

          port {
            container_port = var.container_port
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.github_token.metadata[0].name
            }
          }

          resources {
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }
            limits = {
              cpu    = var.cpu_limit
              memory = var.memory_limit
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = var.container_port
            }
            initial_delay_seconds = 10
            period_seconds        = 30
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = var.container_port
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

# Service (LoadBalancer)
resource "kubernetes_service" "api_gateway" {
  metadata {
    name      = "api-gateway-service"
    namespace = kubernetes_namespace.app.metadata[0].name

    labels = {
      app     = "api-gateway"
      managed = "terraform"
    }
  }

  spec {
    type = "LoadBalancer"

    selector = {
      app = "api-gateway"
    }

    port {
      port        = var.service_port
      target_port = var.container_port
      protocol    = "TCP"
    }
  }
}

# Horizontal Pod Autoscaler
resource "kubernetes_horizontal_pod_autoscaler_v2" "api_gateway" {
  metadata {
    name      = "api-gateway-hpa"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  spec {
    min_replicas = var.hpa_min_replicas
    max_replicas = var.hpa_max_replicas

    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.api_gateway.metadata[0].name
    }

    metric {
      type = "Resource"

      resource {
        name = "cpu"

        target {
          type                = "Utilization"
          average_utilization = var.hpa_cpu_target
        }
      }
    }
  }
}
