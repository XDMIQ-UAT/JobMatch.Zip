#!/bin/bash
# GCP VM Setup Script for JobMatch Platform
# Free Tier Compatible with Ollama Support

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
ZONE="${GCP_ZONE:-us-central1-a}"
VM_NAME="${VM_NAME:-jobmatch-vm}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-small}"  # e2-small: 2 vCPU, 2GB RAM (within free tier credits)
DISK_SIZE="${DISK_SIZE:-30GB}"
IMAGE_FAMILY="${IMAGE_FAMILY:-ubuntu-2204-lts}"
IMAGE_PROJECT="${IMAGE_PROJECT:-ubuntu-os-cloud}"

echo "🚀 Setting up GCP VM for JobMatch Platform..."
echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"
echo "VM Name: $VM_NAME"
echo "Machine Type: $MACHINE_TYPE"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Create VM with startup script
echo "📦 Creating VM instance..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-tier=PREMIUM \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=$(gcloud iam service-accounts list --filter="displayName:Compute Engine default service account" --format="value(email)") \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=$VM_NAME,image=projects/$IMAGE_PROJECT/global/images/family/$IMAGE_FAMILY,mode=rw,size=$DISK_SIZE,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-standard \
    --metadata-from-file startup-script=scripts/vm-startup-script.sh \
    --metadata=ENVIRONMENT=production

# Wait for VM to be ready
echo "⏳ Waiting for VM to be ready..."
sleep 30

# Get VM IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "✅ VM created successfully!"
echo "🌐 External IP: $VM_IP"

# Create firewall rules if they don't exist
echo "🔥 Configuring firewall rules..."
gcloud compute firewall-rules create allow-http --allow tcp:80 --source-ranges 0.0.0.0/0 --target-tags http-server --description "Allow HTTP traffic" 2>/dev/null || echo "Firewall rule 'allow-http' already exists"
gcloud compute firewall-rules create allow-https --allow tcp:443 --source-ranges 0.0.0.0/0 --target-tags https-server --description "Allow HTTPS traffic" 2>/dev/null || echo "Firewall rule 'allow-https' already exists"
gcloud compute firewall-rules create allow-app --allow tcp:8000,tcp:3000 --source-ranges 0.0.0.0/0 --target-tags http-server --description "Allow app ports" 2>/dev/null || echo "Firewall rule 'allow-app' already exists"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "2. Check startup script logs: sudo journalctl -u google-startup-scripts.service"
echo "3. Deploy application: See scripts/deploy-to-vm.sh"
echo ""
echo "🌐 VM IP Address: $VM_IP"
echo "💾 Save this IP for DNS configuration"

