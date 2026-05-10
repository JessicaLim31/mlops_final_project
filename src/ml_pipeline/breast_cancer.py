import os
import json
import joblib
import boto3
import io
from datetime import datetime
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

model_path = "models/cancer_model.pkl"
metrics_path = "models/metrics.json"
metadata_path = "models/metadata.json"
testdata_path = "models/test_data.pkl"
s3_bucket = "mlops-final-project331"


def train_model():
    os.makedirs("models", exist_ok=True)
    data = load_breast_cancer()
    
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    
    clf = LogisticRegression(max_iter=2000)
    clf.fit(X_train, y_train)
    
    joblib.dump(clf, model_path)
    print(f"model saved to {model_path}")
    
    joblib.dump((X_test, y_test), testdata_path)
    print(f"test data saved to {testdata_path}")
    
    #  upload test data to S3 for Airflow
    s3 = boto3.client("s3")
    s3.upload_file(testdata_path, s3_bucket, "data/test_data.pkl")
    print(f"[train_model] upload test data to s3://{s3_bucket}/data/test_data.pkl")

def eval_model():
    clf = joblib.load(model_path)
    X_test, y_test = joblib.load (testdata_path)
    
    y_hat = clf.predict(X_test)
    accuracy = round(accuracy_score(y_test,y_hat),3)
    print(f"[eval_model] Accuracy: {accuracy}")
    
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    metrics = {"accuracy": accuracy}
    with open (metrics_path,"w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[eval_model] saved metrics to {metrics_path}")
    
    metadata = {
        "model_version": version,
        "dataset":"breast_cancer",
        "model_type": "logistic_regression",
        "accuracy": accuracy
    }
    
    with open(metadata_path,"w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[eval_model] Saved metadata to {metadata_path}")
    

def promote_model():
    with open(metrics_path, "r") as f:
        metrics =  json.load (f)
        
    accuracy = metrics ["accuracy"]
    if accuracy < 0.94:
        raise ValueError(f"Model accuracy {accuracy} is below threshold.")
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    s3 = boto3.client("s3")
    version = metadata["model_version"]
    s3_prefix = f"models/{version}"
    artifacts = [
        (model_path, f"{s3_prefix}/model.pkl"),
        (metrics_path, f"{s3_prefix}/metrics.json"),
        (metadata_path, f"{s3_prefix}/metadata.json")
    ]
    
    for local_path, s3_key in artifacts:
        s3.upload_file(local_path, s3_bucket, s3_key)
        print(f"[promote_model] uploaded to s3://{s3_bucket}/{s3_key}")
        
    s3.upload_file(model_path, s3_bucket, "models/latest/model.pkl")
    print(f"[promote_model] uploaded to s3://{s3_bucket}/models/latest/model.pkl")
    
    print("[promote_model] Promotion complete.")

def sqs_queue():
    QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/701262207008/test-queue"

    s3 = boto3.client("s3")
    sqs = boto3.client("sqs")

    obj = s3.get_object(Bucket=s3_bucket, Key="data/test_data.pkl")
    X_test, _ = joblib.load(io.BytesIO(obj["Body"].read()))
    print(f"[sqs_queue] Loaded {len(X_test)} test data from S3.")

    if len(X_test) == 0:
        raise ValueError("[sqs_queue] No test data found in S3. Aborting SQS send.")

    for i, features in enumerate(X_test):
        msg = {
            "record_id": f"test_data{i:03d}",
            "features": features.tolist()
        }
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(msg))
        print(f"[sqs_queue] Sent {i + 1}/{len(X_test)}")

    print(f"[sqs_queue] Done. {len(X_test)} sample sent to SQS.")
