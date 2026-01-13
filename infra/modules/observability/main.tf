# --- 1. DynamoDB: The Audit Ledger ---
resource "aws_dynamodb_table" "pipeline_audit" {
  name         = "${var.project_name}-${var.environment}-pipeline-audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_run_id" # e.g., yellow_taxi_silver#uuid
  range_key    = "timestamp"

  attribute {
    name = "job_run_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Environment = "LocalStack"
    Layer       = "Observability"
  }
}

# --- 2. SNS: The Alert Entry Point ---
resource "aws_sns_topic" "pipeline_alerts" {
  name = "${var.project_name}-${var.environment}-pipeline-alerts"

}

# --- 3. SQS: The Reliable Queue ---
resource "aws_sqs_queue" "pipeline_alerts_queue" {
  name = "${var.project_name}-${var.environment}-pipeline-alerts-queue"
}

# --- 4. The Subscription: Fan-out from SNS to SQS ---
resource "aws_sns_topic_subscription" "sns_to_sqs" {
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.pipeline_alerts_queue.arn
}

# --- 5. Policy: Allow SNS to write to SQS ---
resource "aws_sqs_queue_policy" "sns_publish_to_sqs" {
  queue_url = aws_sqs_queue.pipeline_alerts_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.pipeline_alerts_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.pipeline_alerts.arn
          }
        }
      }
    ]
  })
}

# Output the ARN for .env file
output "sns_topic_arn" {
  value = aws_sns_topic.pipeline_alerts.arn
}
