locals {
  name_prefix = "${var.project}-${var.environment}"
  db_identifier = coalesce(
    var.db_identifier,
    "${local.name_prefix}-postgres"
  )

  tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      Terraform   = "true"
    },
    var.tags
  )
}

resource "aws_db_subnet_group" "postgres" {
  name       = "${local.db_identifier}-subnets"
  subnet_ids = var.db_subnet_ids

  tags = merge(
    local.tags,
    {
      Name = "${local.db_identifier}-subnet-group"
    }
  )
}

resource "aws_security_group" "postgres" {
  name        = "${local.db_identifier}-sg"
  description = "Security group for the ${local.db_identifier} PostgreSQL instance"
  vpc_id      = var.vpc_id

  ingress {
    description      = "PostgreSQL access from allowed CIDR blocks"
    from_port        = var.port
    to_port          = var.port
    protocol         = "tcp"
    cidr_blocks      = var.allowed_cidr_blocks
    ipv6_cidr_blocks = []
    prefix_list_ids  = []
    security_groups  = []
  }

  dynamic "ingress" {
    for_each = var.allowed_security_group_ids
    content {
      description = "PostgreSQL access from security group ${ingress.value}"
      from_port   = var.port
      to_port     = var.port
      protocol    = "tcp"
      security_groups = [
        ingress.value
      ]
    }
  }

  egress {
    description      = "Allow all outbound traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = "${local.db_identifier}-sg"
    }
  )
}

resource "aws_db_instance" "postgres" {
  identifier = local.db_identifier

  engine         = "postgres"
  engine_version = var.engine_version

  instance_class        = var.db_instance_class
  db_name               = var.db_name
  username              = var.db_username
  password              = var.db_password
  port                  = var.port
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = true
  kms_key_id            = var.kms_key_id
  iops                  = var.iops

  db_subnet_group_name = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = concat(
    [aws_security_group.postgres.id],
    var.additional_security_group_ids
  )

  multi_az                   = var.multi_az
  publicly_accessible        = var.publicly_accessible
  backup_retention_period    = var.backup_retention_period
  backup_window              = var.preferred_backup_window
  maintenance_window         = var.preferred_maintenance_window
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  copy_tags_to_snapshot      = var.copy_tags_to_snapshot

  monitoring_interval = var.monitoring_interval

  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  performance_insights_kms_key_id       = var.performance_insights_enabled ? var.performance_insights_kms_key_id : null

  apply_immediately         = var.apply_immediately
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : var.final_snapshot_identifier

  parameter_group_name = var.db_parameter_group_name

  tags = merge(
    local.tags,
    {
      Name = local.db_identifier
    }
  )
}
