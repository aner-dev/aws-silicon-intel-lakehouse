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
# scaling 
vertical vs horizontal scaling 
## load balancing 
  
# regions
japan, USA, UK; in the cloud, this countries are their **regions** 
Massive geographically separate areas where *cloud-providers* has its data centers.
Us-East-1 e.g. 
## AZs / Availability Zones 
They are 1 or more actual physical data centers within a specific **region** 
  - Separated for miles, far enough  
Designed to be completely independent one from each other [[decopuling]]
  - each one have their own networking, cooling, power. 
- If one fails won't afect the other
### interview questions 
- Question: "How would you design an application it doesn't go down if a data center fails?"
- Answer: "I would deploy a server across multiple **Availability zones** and use a **Load Balancer** to distribute the traffic"


# public, private and hybrid cloud 
- How you're going to use cloud? 

![diagram](public_privacy_cloud.png)
## hybrid
Approach that the most large companies do:
keep their most **sensitive data** safe on their own *private servers*
### interview questions 
- Question: "Why would a bank choose a *hybrid cloud model*"
- Answer: "well, they'd keep the most sensitive data in their private cloud for security. But they'd use the *public cloud* for *less sensitive things/data*; like their marketing webiste for instance."


# networking
- **subnet**: a small chunk of the VPC 
  - a way to organize *networking* into smaller manageable pieces
  - Equivalent of assigning *different IP addresses* to your subnets
# security 
IAM roles 
abstraction of 'permission given' of aws 
example IAM key: `Access to Room 502 only, expires at 5 PM. today`
