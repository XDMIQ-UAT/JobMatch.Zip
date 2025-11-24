#!/bin/bash
# Complete deployment script with DNS configuration for jobmatch.zip

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
DOMAIN="${DOMAIN:-jobmatch.zip}"
GCP_PROJECT_ID="${GCP_PROJECT_ID}"

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID not set"
    exit 1
fi

echo "🚀 Deploying JobMatch Platform to https://$DOMAIN"
echo ""

# Step 1: Create VM if it doesn't exist
echo "📦 Step 1: Checking VM..."
if ! gcloud compute instances describe $VM_NAME --zone=$ZONE &>/dev/null; then
    echo "Creating VM..."
    ./scripts/gcp-vm-setup.sh
else
    echo "VM already exists"
fi

# Get VM IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM IP: $VM_IP"
echo ""

# Step 2: Deploy application
echo "📤 Step 2: Deploying application..."
export VM_IP=$VM_IP
./scripts/deploy-to-vm.sh
echo ""

# Step 3: Configure DNS (if using Cloud DNS)
echo "🌐 Step 3: Configuring DNS..."
if gcloud dns managed-zones list --format="value(name)" | grep -q "jobmatch"; then
    echo "DNS zone exists"
else
    echo "Creating DNS zone..."
    gcloud dns managed-zones create jobmatch-zone \
        --dns-name="$DOMAIN" \
        --description="DNS zone for JobMatch Platform"
fi

ZONE_NAME=$(gcloud dns managed-zones list --filter="dnsName:$DOMAIN" --format="value(name)" | head -1)

if [ -n "$ZONE_NAME" ]; then
    # Add A records
    gcloud dns record-sets create $DOMAIN. \
        --zone=$ZONE_NAME \
        --type=A \
        --ttl=300 \
        --rrdatas=$VM_IP 2>/dev/null || \
    gcloud dns record-sets update $DOMAIN. \
        --zone=$ZONE_NAME \
        --type=A \
        --ttl=300 \
        --rrdatas=$VM_IP
    
    gcloud dns record-sets create www.$DOMAIN. \
        --zone=$ZONE_NAME \
        --type=A \
        --ttl=300 \
        --rrdatas=$VM_IP 2>/dev/null || \
    gcloud dns record-sets update www.$DOMAIN. \
        --zone=$ZONE_NAME \
        --type=A \
        --ttl=300 \
        --rrdatas=$VM_IP
    
    echo "✅ DNS records created/updated"
    echo "   Name servers:"
    gcloud dns managed-zones describe $ZONE_NAME --format="value(nameServers)"
else
    echo "⚠️  DNS zone not found. Please configure DNS manually:"
    echo "   Point $DOMAIN A record to: $VM_IP"
    echo "   Point www.$DOMAIN A record to: $VM_IP"
fi
echo ""

# Step 4: Check for Porkbun credentials
echo "🔐 Step 4: Checking Porkbun credentials..."
CREDENTIALS_FILE="${CREDENTIALS_FILE:-.porkbun-credentials}"
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "⚠️  Porkbun credentials not found"
    echo "   Setting up Porkbun credentials..."
    ./scripts/setup-porkbun-credentials.sh
    if [ $? -ne 0 ]; then
        echo "❌ Failed to set up Porkbun credentials"
        exit 1
    fi
else
    echo "✅ Porkbun credentials found"
fi

# Step 5: Setup HTTPS
echo "🔒 Step 5: Setting up HTTPS with Porkbun SSL..."
sleep 10  # Wait for DNS to propagate a bit
./scripts/setup-https-jobmatch-zip.sh
echo ""

# Step 6: Test deployment
echo "🧪 Step 6: Testing deployment..."
sleep 5
./scripts/test-deployment.sh $VM_IP
echo ""

echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your application:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "📋 Version: REV001"
echo "📋 Health: https://$DOMAIN/health"
echo "📋 API Docs: https://$DOMAIN/api/docs"

