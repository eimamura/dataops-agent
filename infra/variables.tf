variable "aws_region" {
  type        = string
  description = "AWS region where all resources will be created."
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  description = "Optional AWS CLI profile to use for authentication."
  default     = null
}

variable "project" {
  type        = string
  description = "Short name of the project. Used for tagging and resource naming."
}

variable "environment" {
  type        = string
  description = "Deployment environment name (e.g. dev, staging, prod)."
}

variable "db_identifier" {
  type        = string
  description = "Optional identifier for the RDS instance. Defaults to <project>-<environment>-postgres."
  default     = null
}

variable "db_name" {
  type        = string
  description = "Initial PostgreSQL database name."
  default     = "appdb"
}

variable "db_username" {
  type        = string
  description = "Master username for the PostgreSQL instance."
}

variable "db_password" {
  type        = string
  description = "Master password for the PostgreSQL instance."
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class (size) to provision."
  default     = "db.t3.micro"
}

variable "engine_version" {
  type        = string
  description = "PostgreSQL engine version."
  default     = "15.5"
}

variable "allocated_storage" {
  type        = number
  description = "Initial storage size in GiB."
  default     = 20
}

variable "max_allocated_storage" {
  type        = number
  description = "Upper limit for autoscaling storage. Set to null to disable autoscaling."
  default     = null
}

variable "storage_type" {
  type        = string
  description = "The storage type to associate with the DB instance (gp2, gp3, io1, etc.)."
  default     = "gp3"
}

variable "iops" {
  type        = number
  description = "Amount of provisioned IOPS. Only used for gp3/io1/io2."
  default     = null
}

variable "port" {
  type        = number
  description = "Port the database should listen on."
  default     = 5432
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the database should live."
}

variable "db_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for the DB subnet group."
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "List of CIDR blocks that are allowed to connect to the database."
  default     = []
}

variable "allowed_security_group_ids" {
  type        = list(string)
  description = "Existing security group IDs that should be allowed ingress to the database."
  default     = []
}

variable "additional_security_group_ids" {
  type        = list(string)
  description = "Additional security groups to attach to the DB instance (in addition to the one created here)."
  default     = []
}

variable "publicly_accessible" {
  type        = bool
  description = "Whether the DB instance should have a public IP."
  default     = false
}

variable "multi_az" {
  type        = bool
  description = "Enable Multi-AZ deployments for high availability."
  default     = false
}

variable "backup_retention_period" {
  type        = number
  description = "Number of days to retain backups."
  default     = 7
}

variable "preferred_backup_window" {
  type        = string
  description = "Daily time range during which automated backups are created."
  default     = "03:00-06:00"
}

variable "preferred_maintenance_window" {
  type        = string
  description = "Weekly window for maintenance operations."
  default     = "sun:05:00-sun:06:00"
}

variable "auto_minor_version_upgrade" {
  type        = bool
  description = "Enable automatic minor engine version upgrades during maintenance windows."
  default     = true
}

variable "copy_tags_to_snapshot" {
  type        = bool
  description = "Copy all tags from the instance to snapshots."
  default     = true
}

variable "monitoring_interval" {
  type        = number
  description = "Enhanced monitoring interval in seconds. Set to 0 to disable."
  default     = 0
}

variable "performance_insights_enabled" {
  type        = bool
  description = "Toggle Performance Insights collection."
  default     = true
}

variable "performance_insights_retention_period" {
  type        = number
  description = "Number of days to retain Performance Insights data (7 or 731)."
  default     = 7
}

variable "performance_insights_kms_key_id" {
  type        = string
  description = "KMS key for encrypting Performance Insights data."
  default     = null
}

variable "kms_key_id" {
  type        = string
  description = "KMS key for encrypting the database. Defaults to the account managed key when null."
  default     = null
}

variable "db_parameter_group_name" {
  type        = string
  description = "Existing DB parameter group to associate with the instance."
  default     = null
}

variable "apply_immediately" {
  type        = bool
  description = "Apply modifications immediately instead of during the next maintenance window."
  default     = false
}

variable "deletion_protection" {
  type        = bool
  description = "Protect the instance from accidental deletion."
  default     = true
}

variable "skip_final_snapshot" {
  type        = bool
  description = "Skip taking a final snapshot before deletion."
  default     = false
}

variable "final_snapshot_identifier" {
  type        = string
  description = "Identifier for the final snapshot taken before deletion (required when skip_final_snapshot is false)."
  default     = null

  validation {
    condition     = var.skip_final_snapshot || var.final_snapshot_identifier != null
    error_message = "A final_snapshot_identifier must be supplied when skip_final_snapshot is false."
  }
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to all resources."
  default     = {}
}
