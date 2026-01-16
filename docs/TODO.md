# enumerated checklist
IAM Module: Build 3 roles (Bronze, Silver, Observability).
Outputs: Export those Role ARNs.
Compute Module: Assign the correct Role ARN to each Lambda.
Env Vars: Ensure PIPELINE_ALERTS_TOPIC_ARN and AUDIT_TABLE_NAME are present in every Lambda so the ObservabilityManager can work.
## tasks
- [ ] Create the "Assume Role" Policy
- [ ] Define the Bronze Permissions
- [ ] Define the Silver Permissions (Spark/Iceberg)
- create infra/module/compute/main.tf 
  - [ ] role = var.lambda_role_arn: Link the role you just created.
  - [ ] environment { variables = { ... } }: This is where you map the ARNs and Bucket names.
