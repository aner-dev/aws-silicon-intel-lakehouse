# Observability & Monitoring Strategy

| Feature | Service (AWS Docs) | Your Implementation | Purpose |
| :--- | :--- | :--- | :--- |
| **Metrics** | CloudWatch | `metrics` dict in DynamoDB | "How many rows?" "How fast?" |
| **Logs** | CloudWatch Logs | `utils/logging_config.py` | "What happened at 10:01 AM?" |
| **Traces** | X-Ray / ADOT (OTEL) | *None (Not needed yet)* | "Which microservice is slow?" |
| **Audit/State** | DynamoDB + SNS | DynamoDB + SNS | "Did the job succeed? Where did it stop?" |

---

### Implementation Breakdown

* **Custom Metrics:** By storing a metrics dictionary in DynamoDB, you create a lightweight, queryable audit trail of performance without the complexity of full X-Ray implementation.
* **Centralized Logging:** Standardizing through a utility config ensures consistent formatting across all Lambda functions or containers.
* **Audit vs. Tracing:** Note that **Audit/State** is distinct from OpenTelemetry (OTEL); it serves as the "source of truth" for your pipeline's success rather than just performance monitoring.
# Observability of the project
## Data Lineage & Alerting Logic

| Value Source | Destination | Purpose |
| :--- | :--- | :--- |
| **silver_df columns** | S3 / Apache Iceberg | **Data Traceability:** Identifying the origin of a specific row. |
| **metrics dict** | DynamoDB | **Operational Visibility:** High-level counts and performance. |
| **SNS Message** | SQS / Lambda | **Immediate Alerting:** Letting humans know the system broke. |

---

### Logic Overview

* **Iceberg Integration:** Storing source columns in the Silver layer ensures that even after transformations, you can perform "root cause analysis" on the raw data origin.
* **Decoupled Alerting:** Using SNS to SQS/Lambda is a best practice for **Fan-out patterns**, allowing you to send alerts to multiple destinations (like Slack, Email, or PagerDuty) simultaneously.
