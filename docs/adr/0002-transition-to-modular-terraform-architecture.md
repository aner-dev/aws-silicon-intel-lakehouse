# ADR 001: Transition to Modular Terraform Architecture

## Status
Accepted

## Context
The project's infrastructure was initially implemented as a monolithic configuration. As the "Silicon Intel Lakehouse" evolved to include multiple AWS-emulated services (S3, DynamoDB, SNS, SQS, Secrets Manager), the monolithic structure increased cognitive load and the potential blast radius of configuration changes. A single error in the transformation logic could risk the state of the storage layer.

## Decision
After doing a research for best practices in terraform and IaC for Cloud Production environments, I notice that my monolithic approach was incorrect and suboptimal. 
Also I think that it was because I was having a lot of issues and errors at deploying infrastructure by using `make dev`
Thus I have refactored the directory structure of the infrastructure into a **Module-Based Topology**. The system is now partitioned into discrete logical subsystems:

* **Storage Module:** Manages S3 Medallion layers (Bronze/Silver/Gold) and DynamoDB audit tables.
* **Notifications Module:** Handles SNS/SQS alert fan-out logic.
* **Database/Compute Modules:** (Scaffolded) Reserved for stateful services and Lambda-based ingestion.

## Justification & Advantages

### 1. Separation of Concerns (SoC)
By decoupling the **Storage (Data Persistence)** from **Compute/Notifications (Logic)**, we ensure that updates to messaging or compute resources do not interfere with the state of the S3 buckets. This isolation reduces the risk of accidental data deletion during infrastructure refactoring.

### 2. Interface-Driven Design
The use of `variables.tf` (Inputs) and `outputs.tf` (Exports) creates a formal "contract" between the root orchestrator and the subsystems. This makes the data flow (e.g., S3 Bucket ARNs being passed to Lambda functions) explicit and traceable.

### 3. Scalability and Development Velocity
New data layers or services can be added by instantiating new modules without modifying the existing, stable resource blocks. This allows the infrastructure to *scale horizontally*, as the Lakehouse requirements grow in a future cloud migration.

### 4. Environment Portability (Parity)
The modules are designed to be *provider-agnostic*. 
By isolating the LocalStack-specific endpoint configuration in the root `provider.tf`, the core module logic remains identical to what would be deployed in a production AWS environment, ensuring high dev-to-prod parity.
