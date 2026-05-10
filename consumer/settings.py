import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from config import S3_BUCKET, QUEUE_URL

S3_MODEL_KEY = "models/latest/model.pkl"
PREDICTION_PREFIX =  "predictions/"
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "3"))
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "30"))
WAIT_TIME = int(os.getenv("WAIT_TIME", "20"))
