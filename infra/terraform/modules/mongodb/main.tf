resource "aws_docdb_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-docdb-subnet"
  subnet_ids = var.private_subnets
}

resource "aws_security_group" "docdb" {
  name   = "${var.project}-${var.environment}-docdb-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_docdb_cluster" "main" {
  cluster_identifier      = "${var.project}-${var.environment}"
  engine                  = "docdb"
  master_username         = var.db_username
  master_password         = var.db_password
  db_subnet_group_name    = aws_docdb_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.docdb.id]
  skip_final_snapshot     = true  # prod에서는 false로 변경
  backup_retention_period = 7
}

resource "aws_docdb_cluster_instance" "main" {
  count              = 1
  identifier         = "${var.project}-${var.environment}-${count.index}"
  cluster_identifier = aws_docdb_cluster.main.id
  instance_class     = var.instance_class
}
