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
