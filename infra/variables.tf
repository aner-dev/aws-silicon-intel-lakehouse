variable "news_api_key" {
  description = "API Key for News API"
  type        = string
  sensitive   = true # Esto evita que el valor se imprima en los logs de GitHub Actions
}
