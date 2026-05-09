import os

QUEUE_URL = os.getenv("QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/701262207008/test_queue")

S3_BUCKET = os.getenv("S3_BUCKET", "mlops-final-project331")
S3_MODEL_KEY = "models/latest/model.pkl"
PREDICTION_PREFIX =  "predictions/"


MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "3"))
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "30"))
WAIT_TIME = int(os.getenv("WAIT_TIME", "20"))