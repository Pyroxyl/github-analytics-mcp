output "service_url" {
  description = "URL to access the API gateway service"
  value       = "http://localhost:${var.service_port}"
}

output "namespace" {
  description = "Kubernetes namespace where resources are deployed"
  value       = kubernetes_namespace.app.metadata[0].name
}

output "deployment_name" {
  description = "Name of the API gateway deployment"
  value       = kubernetes_deployment.api_gateway.metadata[0].name
}
