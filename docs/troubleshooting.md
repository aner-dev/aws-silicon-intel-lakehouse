# Troubleshooting: Container Registry & Image Migration

## Issue: Spark Image Pull Failure
**Date:** 2026-01-05
**Symptom:** `Error: reading manifest 3.5.0 in docker.io/bitnami/spark: manifest unknown`

### Root Cause Analysis (RCA)
Problem: each `astro dev start` was failing in pulling the 'bitnami/spark' images, with few different syntax tries. 
Cause: As of late 2025/early 2026, Bitnami transitioned their primary Spark OCI artifacts to a commercial subscription model. The public tags on Docker Hub were either deprecated or pointed to empty manifests, causing Podman to fail during the setup of the lakehouse sidecars.

### Resolution
Research Bitnami page on Docker Hub, find that isn't free anymore.
Solution: Pivoted the project infrastructure to use the **official Apache Spark images** maintained by the Apache Software Foundation.

**Changes:**
- Updated `docker-compose.override.yml`:
  - From: `bitnami/spark:3.5.0`
  - To: `docker.io/apache/spark:3.5.0`
- Configured Spark Master/Worker environment variables to match Apache's standard (`SPARK_MODE`).

### Lessons Learned
1. **Prefer Upstream:** Always prefer official technology images (Apache, Postgres) over third-party vendors (Bitnami) unless specific hardening is required.
2. **Registry Specificity:** Use Fully Qualified Image Names (FQIN) in Podman to avoid registry resolution ambiguity.

# Spark & Schema Mismatch
I encountered a schema mismatch crash in Spark while merging Parquet files with inconsistent types. I solved it by overriding the Catalyst Optimizer's default discovery behavior, disabling global schema merging in the session, and enforcing a manual casting strategy in the transformation layer. I then documented the entire meta-explanation in the project's technical docs to prevent future regressions.

# Problem Report: Observability Metadata Collision in Terraform
**Date:** 2026-01-13  
**Status:** Resolved  

---

### Error
* **Error:** `Module not installed` 
* **AttributeError:** Occurred when attempting to access logging attributes within the Lambda consumer.

### Root Cause Analysis (RCA)
1. **Infrastructure:** Attempted to execute `terraform validate` on a new module structure without re-initializing the backend.
2. **Data Logic:** There was a disconnect between the **Producer (Spark Job)** and the **Consumer (Lambda)** regarding how metadata (specifically `execution_id`) was being propagated across the pipeline.

---

### Solution 
> I implemented a **Standardized Lifecycle** for infrastructure changes and a **Context-Aware Logging** pattern.

* **Tooling Fix:** Executed `terraform init` to properly index the new observability module before validation.
* **Code Refactor:** Refactored the Silver transformation layer to **Inject the `execution_id`** into every log entry and data row. This ensures a 1-to-1 correlation between the Spark execution and the downstream Lambda alerts.

---

### Learning
* **Terraform Init Hierarchical Relevance:** Any change to the `module` blocks in the root `main.tf` requires a `terraform init` to map the local directory to the state.
* **Metadata Propagation:** Observability is only as good as the **Correlation ID**. If the ID does not travel seamlessly from the data layer to the application logs, the "audit trail" is broken.
# terraform output vs observability modules (topic_arn)
traceback error:
`module.notifications.aws_sns_topic.pipeline_alerts`
`module.observability.aws_sns_topic.pipeline_alerts`
Terraform is doing exactly what I asked:
2 modules
Each declares an aws_sns_topic
Therefore: two physical SNS topics

This violates a fundamental IaC principle:
*One physical resource must be owned by exactly one module.*
## infra/modules/observability 
observability module CONSUME sns_topic_arn, it accepts it as *input*.
It must NOT create SNS topics. 
