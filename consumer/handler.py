import json
import joblib
import boto3
from datetime import datetime, timezone
from settings import S3_BUCKET, S3_MODEL_KEY, PREDICTION_PREFIX

s3 = boto3.client("s3")

LOCAL_MODEL_PATH = "/tmp/model.pkl"
_model = None

def load_model():
    """ Load model from S3, then cached in memory"""
    
    global _model
    
    if _model is None:
        print(f"Downloading model from s3://{S3_BUCKET}/{S3_MODEL_KEY}")
        
        s3.download_file(
            S3_BUCKET,
            S3_MODEL_KEY,
            LOCAL_MODEL_PATH
        )
        
        
        _model = joblib.load(LOCAL_MODEL_PATH)
        print("Model loaded successfully")
        
    return _model

def handle_message(msg_body: dict):
    """ Actual application logic for single inference """
    
    record_id = msg_body.get("record_id")
    features = msg_body.get("features")
    
    if not record_id:
        raise ValueError("Missing record_id in message")
    
    if features is None:
        raise ValueError("Missing features in message")
    
    model = load_model()
    prediction = int(model.predict([features])[0])

    result = {
        "record_id": record_id,
        "prediction": prediction,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    pred_key = f"{PREDICTION_PREFIX}{record_id}.json"
    
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=pred_key,
        Body=json.dumps(result),
        ContentType="application/json"
    )
    
    print(f"Saved prediction to s3://{S3_BUCKET}/{pred_key}")
    
    return result