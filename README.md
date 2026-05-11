# Final Project: Building an Asynchronous AI Inference System

In this final project, you will design and build an end-to-end ML system that trains a breast cancer classification model and serves inference at scale combines: 
● orchestration (Airflow) 
● object storage (S3) 
● message queues (SQS) 
● scalable compute (Kubernetes)  

---
Archictecture Overview
##  Project Structure

```
mlops_final_project/
├── dags/                             # Airflow DAGs
│   └── breast_cancer_pipeline.py     # Airflow DAG: train → evaluate → promote → send SQS messages
|
├── consumer/
│   ├── consumer.py                   # SQS polling + inference app
│   ├── Dockerfile                    # Container image for the consumer
│   └── requirements.txt              # Consumer python dependencies
|
├── kubernates/   
│   └── deployment.yaml               # EKS Deployment (2 replicas)
|
├── src/ml_pipeline/
|    └── breast_cancer.py             # Training, evaluation, promotion, and SQS producer logic
|
├── cluster.yaml                      # EKS cluster config
├── setup_airflow.sh                  # one-time Airflow setup script
└── requirements.txt                  # Python dependencies
```
## Prerequisites

- An S3 Bucket created
- An SQS Queue Created ( optional: add another DLQ)
- Python 3.12
---


## Step 1. Environment Setup

We use **one virtual environment** for all labs.
1. Clone the repo
1. Create and activate:

```
python3.12 -m venv .venv
source ./venvs/bin/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

⚠️ The `requirements.txt` pins **Airflow 2.10.2**. If you are not on Python 3.10, update the constraints line to match (`constraints-3.9.txt` or `constraints-3.11.txt`).  

3. Update Confid
- Update your SQS URL and S3 bucket in config.py and kubernetes/deployment.yaml
- Update repo name in kubernetes/deployment.yaml
---
## Stap 2. Setup ECR and Docker
1. Navigate to elastic container registry in AWS
2. Create a new registry. You can name it whatever you would like.
3. After creating the registry. View the registry and look at the push commands to push a new docker file. We will be using these in the next step.
4. Follow the instructions from Push Commands to build Dockers image
5. You should be able to see the docker file within the registry when completed

---
## Step 3. Kubernetes set up

### Approach 1:  ECR + ECS 
### ECS Setup
1. We now need to create a new ECS cluster. This cluster can be used to run and manage different containers
2. Click create cluster and name the cluster. Make sure to build it with “fargate and managed”.
3. Now that we have fargate setup. We need to create tasks that can be referenced by the cluster. To do this we will use task definition.
4. Navigate to task definitions within ECS and create a new task definition.
   -  Define a task family
   -  Launch type: **Fargate**
   - Use labrole for the task role and task execution role
   - Under Container you can name the container what you want, but be sure to reference the container to the proper one in your ECR. This is the container we just uploaded and it should be set as the image-URI in the task
   - Make sure to open up the network to all traffic.
   - Default resources and storage should be fine
5. Now we want to create a new service within the ECS cluster. Navigate to your cluster and add the new task.
   - Make sure you specify it as a service
   - You do not need to specify a capacity service. Just pick the launch type with type fargate.
   - Under Family you should be able to find the task definition you just made.
   
6. Now we have all ECR and ECS  set up.

### Approach 2: ECR + EKS (Kubernetes)
### EKS Setup
⚠️ Note: Use AWS CloudShell for EKS - Cloud 9 will expire during cluster creation

- In CloudShell
``
git clone  git@github.com:JessicaLim31/mlops_final_project.git
cd mlops_final_project
``
- Update your account ID
```
sed -i 's/<account number>/YOUR_ACTUAL_ACCOUNT_ID/' ~/mlops_final_project/setup_eks.sh
```

- Run the setup script
```
chmod +x setup_eks.sh
./setup_eks.sh

```
---
## Step 4. Airflow Setup (one time)

- Run the setup script:

```
source./setup_airflow.sh
```
- Create User

```
airflow users create \
--username admin \
--firstname Airflow \
--lastname Admin \
--role Admin \
--email admin@example.com \
--password admin

```

- Start Airflow
```
airflow webserver --port 8080
```

- Open Another Terminal, run scheduler
```
cd mlops_final_project
source./setup_airflow.sh
airflow scheduler
```
- Then visit http://<your_ip_address>:8080
- Login: admin / admin
  
- You will see your pipeline DAG, click Trigger DAG to run manually

---
## Step 5. Verified the workflow

- Check if SQS is empty, and verify log if it run
- Verify EKS or ECS log
- Check S3 bucket if model, data and prediction file in there
- Check prediction result in the folder

---

## Step 6. Try to scale replica
- ECS in Cloud 9
```
# Scale up
aws ecs update-service --cluster final-consumer-cluster \
  --service consumer-service --desired-count 4

# Scale down
aws ecs update-service --cluster final-consumer-cluster \
  --service consumer-service --desired-count 2
```
- EKS in CloudShell
```
# Scale up
kubectl scale deployment sqs-consumer --replicas=4
kubectl get pods

# Scale down
kubectl scale deployment sqs-consumer --replicas=2
```

--------------------------------------------------
## Clean Up AWS

Delete EKS cluster
```
eksctl delete cluster --name <cluster name> --region us-east-1
```
Stop ECS service
```
aws ecs update-service --cluster <cluster name> \
  --service consumer-service --desired-count 0
```
Delete ECR repository
```
aws ecr delete-repository --repository-name <repo name> \
  --region us-east-1 --force
```

Purge SQS queue
```
aws sqs purge-queue \
  --queue-url https://sqs.us-east-1.amazonaws.com/<Account number>/test-queue
```
