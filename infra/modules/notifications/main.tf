# 1. THE TOPIC (The Broadcaster)
resource "aws_sns_topic" "alerts" {
  name = var.alerts_topic_name
  tags = var.tags
}

# 2. THE QUEUE (The Storage for Alerts)
resource "aws_sqs_queue" "spark_alerts_queue" {
  name                      = "${var.alerts_topic_name}-queue"
  delay_seconds             = 0
  message_retention_seconds = 345600 # 4 days
  receive_wait_time_seconds = 10     # Long polling
}

# 3. THE SUBSCRIPTION (The Connection)
resource "aws_sns_topic_subscription" "spark_alerts_subscription" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.spark_alerts_queue.arn
}

# 4. THE SECURITY GATEKEEPER (Critical!)
# This allows SNS to send messages into SQS
resource "aws_sqs_queue_policy" "allow_sns" {
  queue_url = aws_sqs_queue.spark_alerts_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowSNSPublishToSQS"
        Effect    = "Allow"
        Principal = { Service = "sns.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.spark_alerts_queue.arn
        Condition = {
          ArnEquals = { "aws:SourceArn" = aws_sns_topic.alerts.arn }
        }
      }
    ]
  })
}

# To send an Email/Slack alert
resource "aws_sns_topic_subscription" "email_target" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "your-email@example.com"
}
