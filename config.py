import os

# Update this before running the code

S3_BUCKET = os.getenv("S3_BUCKET", "mlops-final-project331")
QUEUE_URL = os.getenv("QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/701262207008/test-queue")
EOF
