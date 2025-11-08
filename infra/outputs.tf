output "db_instance_identifier" {
  description = "Identifier of the created PostgreSQL instance."
  value       = aws_db_instance.postgres.id
}

output "db_instance_arn" {
  description = "ARN of the PostgreSQL instance."
  value       = aws_db_instance.postgres.arn
}

output "db_instance_endpoint" {
  description = "Connection endpoint for the PostgreSQL instance."
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "db_security_group_id" {
  description = "ID of the security group controlling database access."
  value       = aws_security_group.postgres.id
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group."
  value       = aws_db_subnet_group.postgres.name
}
