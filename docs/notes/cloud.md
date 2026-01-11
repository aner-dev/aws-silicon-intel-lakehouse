# 5 most relevant skills for aws jobs
terraform
python
CI/CD (github actions, gitlab, jenkins)
k8s / kubernetes (kind)
networking
# AWS 
## account ID relevance (terraform / .tf files)
In AWS, the Account ID (a 12-digit number) is the "DNA" of your infrastructure.
Without it, I cannot build a valid ARN (Amazon Resource Name).
Localstack *non-standard configuration*: 
  - LocalStack isn't a real account; it defaults to 000000000000.
  - If Terraform tries to "verify" the account identity against AWS's real servers, the request will fail because you aren't actually connected to the internet-based AWS API.
  - I skip it locally to keep the "engine" running, but knowing that in a professional cloud environment, I should remove that line, so Terraform can map the IAM policies to the correct, unique Account ID.
