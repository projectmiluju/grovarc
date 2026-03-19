resource "aws_security_group" "kafka" {
  name   = "${var.project}-${var.environment}-kafka-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  ingress {
    from_port   = 9094
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_msk_cluster" "main" {
  cluster_name           = "${var.project}-${var.environment}"
  kafka_version          = var.kafka_version
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type   = var.instance_type
    client_subnets  = slice(var.private_subnets, 0, 2)
    security_groups = [aws_security_group.kafka.id]

    storage_info {
      ebs_storage_info { volume_size = 20 }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS_PLAINTEXT"
      in_cluster    = true
    }
  }
}
