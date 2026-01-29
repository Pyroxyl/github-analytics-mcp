variable "namespace_name" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "github-analytics"
}

variable "api_replicas" {
  description = "Number of API gateway replicas"
  type        = number
  default     = 2
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "image_name" {
  description = "Docker image name for the API gateway"
  type        = string
  default     = "github-analytics-api"
}

variable "container_port" {
  description = "Container port for the API gateway"
  type        = number
  default     = 8080
}

variable "service_port" {
  description = "Service port exposed externally"
  type        = number
  default     = 80
}

variable "cpu_request" {
  description = "CPU resource request"
  type        = string
  default     = "100m"
}

variable "memory_request" {
  description = "Memory resource request"
  type        = string
  default     = "128Mi"
}

variable "cpu_limit" {
  description = "CPU resource limit"
  type        = string
  default     = "500m"
}

variable "memory_limit" {
  description = "Memory resource limit"
  type        = string
  default     = "256Mi"
}

variable "hpa_min_replicas" {
  description = "Minimum replicas for HPA"
  type        = number
  default     = 2
}

variable "hpa_max_replicas" {
  description = "Maximum replicas for HPA"
  type        = number
  default     = 5
}

variable "hpa_cpu_target" {
  description = "Target CPU utilization percentage for HPA"
  type        = number
  default     = 70
}
