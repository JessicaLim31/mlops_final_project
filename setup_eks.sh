## Update following before running
ACCOUNT_ID="701262207008"

# Install sksctl
curl --silent --location \
  "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" \
  | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create Cluster
eksctl create cluster -f cluster.yaml

# Deploy EKS 
kubectl apply -f kubernates/deployment.yaml

# Create ECR pull secret
aws ecr get-login-password --region us-east-1 | \
  kubectl create secret docker-registry ecr-secret \
  --docker-server=${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region us-east-1)
  
kubectl patch deployment sqs-consumer \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"ecr-secret"}]}}}}'

# Verify if pods are running
kubectl get pods
