files related: `src/utils/observability.py` `tests/test_observability.py`

# What does the script? 
* **Job State Management | Pipeline Audit Trail**

* This script acts as a 'State Producer'
  * Recording granular execution metadata to DynamoDB and broadcasting failure signals via SNS.
* In a production environment, this allows the system to have an 'active orchestration', rather than a 'passive logging'. 
  * Where downstream consumers automatically respond to these signals to ensure high availability.
### Observability 
To know at a glance if the heart of your pipeline is beating. If DynamoDB shows 100 "Started" jobs but 0 "Success" jobs, you know the system is hung.

### Idempotency 
If your script crashes at month 5 of 12, you check DynamoDB. You see months 1-4 are "SUCCESS," so you only restart from month 5. This saves thousands of dollars in cloud costs.

### Decoupling 
By sending errors to SNS, your ingestion script doesn't need to know how to send an email or an SMS. It just "screams," and the infrastructure handles the rest.

## Production-Grade Implementations & Improvements
* In a production environment, the observability lifecycle would be "closed" by a downstream consumer. Current manual verification would be replaced by:

* **Automated Alerting (Lambda Consumer):**
  * **Logic:** An AWS Lambda function triggered by the SQS queue.
  * **Implementation:** The Lambda parses failure signals to route alerts to Slack or PagerDuty for immediate intervention.

* **Proactive Monitoring (CloudWatch Alarms):**
  * **Logic:** Emitting custom metrics (e.g., `JobFailureCount`) alongside DynamoDB writes.
  * **Implementation:** CloudWatch Alarms trigger automated notifications if error thresholds are exceeded, ensuring system-wide health visibility.

* **Self-Healing Pipelines (Auto-Remediation):**
  * **Logic:** Downstream services query the DynamoDB 'State Store' for failed job IDs.
  * **Implementation:** Automated retry logic can re-trigger specific batches without manual developer input, improving the pipeline's resilience.

# Refactor of the script (2025-01-14)
1. Performance: "Warm Start" Optimization
  - By moving the boto3 initialization to the Global Scope, you stopped the "Handshake Tax." 
    - The code no longer wastes time resolving DNS and establishing TCP connections on every single function call.
2. Sustainability: "TTL" Implementation
  - Used `Terraform` to enable TTL and Python to calculate the Epoch timestamp, ensuring the project stays lean without manual maintenance.
    - Transformed the database from a "growing cost" into a "self-cleaning system.
3. Architecture: "Fan-out" Readiness
  - Routing failures through SNS instead of direct calls, madding the system "Pluggable." 
    - Today it sends an alert to SQS; tomorrow, I can add an Email or Slack subscriber in `Terraform` without changing a single line of Python code.

> [!abstract] Key Fundamental: Connection Pooling
> Initializing `boto3.client` in global scope keeps the TCP socket open across Lambda warm-starts, reducing latency.
# AWS vs FOSS alternatives implementations (Graphana)
the cost of having a developer maintaining the required infrastructure for a FOSS tools oriented workload, and even a hosting service to keep running the server, would be a negative trade-off compared to use aws services
core factors: maintenance, reliability, integration, scaling

# 3 pillars of observability 
Metrics: (Numbers) How long did it take?

Logs: (Text) The detailed technical errors.

Traces: (Path) How did the data move from S3 to SNS to SQS?
## future improvement (modularization)
utils/
 ├── observability/
 │    ├── notifier.py (SNS logic)
 │    ├── audit.py    (DynamoDB logic)
 │    └── logger.py   (CloudWatch logic)
