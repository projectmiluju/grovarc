#!/bin/bash
# Terraform 상태 파일 저장용 S3 + DynamoDB 초기 생성 스크립트
# 최초 1회만 실행

set -e

REGION="ap-northeast-2"
BUCKET="grovarc-tfstate-dev"
TABLE="grovarc-tfstate-lock"

echo "▶ S3 버킷 생성: $BUCKET"
aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"

aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "$BUCKET" \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'

echo "▶ DynamoDB 테이블 생성: $TABLE"
aws dynamodb create-table \
  --table-name "$TABLE" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "$REGION"

echo "✅ 완료. 이제 terraform init을 실행하세요."
