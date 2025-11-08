# AWS PostgreSQL RDS Terraform Module

Infrastructure-as-code template that provisions an Amazon RDS PostgreSQL instance with secure networking defaults. It creates the DB subnet group, a restrictive security group, and a parameterized DB instance so environments can be spun up consistently.

## Prerequisites
- Terraform CLI v1.5+  
- AWS account credentials available via environment variables or an AWS CLI profile  
- Existing VPC with at least two private subnets for the DB subnet group

## Files
- `providers.tf` – Terraform and AWS provider configuration  
- `variables.tf` – All tunable inputs with descriptions and defaults  
- `main.tf` – Resources: subnet group, security group, and RDS instance  
- `outputs.tf` – Connection details and identifiers  
- `README.md` – Usage guide (this file)

## Usage
1. Populate a `terraform.tfvars` (or use CLI `-var` flags) similar to the example below.  
2. Run `terraform init` to download providers.  
3. Run `terraform plan` to review the infrastructure changes.  
4. Run `terraform apply` when satisfied with the plan.

### Example `terraform.tfvars`
```hcl
project      = "dataops"
environment  = "dev"
aws_region   = "us-east-1"
db_username  = "dbadmin"
db_password  = "change-me"
vpc_id       = "vpc-0123456789abcdef0"
db_subnet_ids = [
  "subnet-aaa...",
  "subnet-bbb..."
]
allowed_cidr_blocks = ["10.0.0.0/24"]
multi_az            = true
allocated_storage   = 50
```

Sensitive values such as `db_password` should be stored securely (e.g., `TF_VAR_db_password` environment variable, Vault, or encrypted variable files) and never committed to version control.

## Helpful Commands
- `terraform fmt` – Auto-format Terraform files.  
- `terraform validate` – Basic static validation of the configuration.  
- `terraform plan -var-file="env/dev.tfvars"` – Plan against a specific environment configuration.  
- `terraform apply -var-file="env/dev.tfvars"` – Apply changes for that environment.  
- `terraform destroy -var-file="env/dev.tfvars"` – Tear down the stack (requires `skip_final_snapshot = true` or providing `final_snapshot_identifier`).

## Inputs Overview
Refer to `variables.tf` for full descriptions. Key inputs include:
- Networking: `vpc_id`, `db_subnet_ids`, `allowed_cidr_blocks`, `allowed_security_group_ids`, `additional_security_group_ids`  
- Database sizing: `db_instance_class`, `allocated_storage`, `max_allocated_storage`, `storage_type`, `iops`  
- Availability & maintenance: `multi_az`, `backup_retention_period`, `preferred_backup_window`, `preferred_maintenance_window`, `auto_minor_version_upgrade`  
- Security: `kms_key_id`, `performance_insights_kms_key_id`, `deletion_protection`, `skip_final_snapshot`, `final_snapshot_identifier`

## Outputs
- `db_instance_identifier` – RDS identifier used in AWS Console/CLI.  
- `db_instance_arn` – ARN for IAM referencing.  
- `db_instance_endpoint` – Hostname:port for connecting (marked sensitive).  
- `db_security_group_id` – Security group controlling inbound access.  
- `db_subnet_group_name` – Subnet group assigned to the instance.
