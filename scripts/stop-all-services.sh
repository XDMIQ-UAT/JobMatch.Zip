#!/bin/bash
# Manual script to stop all GCP services in a project
# Useful for emergency shutdown or testing

set -e

PROJECT_ID="${GCP_PROJECT_ID:-futurelink}"

echo "🛑 Stopping all services in project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Stop all Compute Engine VMs
echo "🖥️  Stopping Compute Engine VMs..."
ZONES=$(gcloud compute zones list --format="value(name)" --project=$PROJECT_ID)

for zone in $ZONES; do
    INSTANCES=$(gcloud compute instances list --filter="status:RUNNING" --format="value(name)" --zones=$zone --project=$PROJECT_ID)
    
    for instance in $INSTANCES; do
        if [ -n "$instance" ]; then
            echo "  Stopping VM: $instance in $zone"
            gcloud compute instances stop $instance --zone=$zone --project=$PROJECT_ID --quiet || true
        fi
    done
done

# Scale down Cloud Run services
echo "☁️  Scaling down Cloud Run services..."
SERVICES=$(gcloud run services list --format="value(name,region)" --project=$PROJECT_ID)

while IFS=$'\t' read -r service region; do
    if [ -n "$service" ] && [ -n "$region" ]; then
        echo "  Scaling down Cloud Run service: $service in $region"
        gcloud run services update $service \
            --region=$region \
            --min-instances=0 \
            --max-instances=0 \
            --project=$PROJECT_ID \
            --quiet || true
    fi
done <<< "$SERVICES"

# Stop Cloud SQL instances (optional - commented out to prevent accidental data loss)
# echo "🗄️  Stopping Cloud SQL instances..."
# INSTANCES=$(gcloud sql instances list --format="value(name)" --project=$PROJECT_ID)
# for instance in $INSTANCES; do
#     if [ -n "$instance" ]; then
#         echo "  Stopping Cloud SQL instance: $instance"
#         gcloud sql instances patch $instance --activation-policy=NEVER --project=$PROJECT_ID || true
#     fi
# done

echo ""
echo "✅ All services stopped!"
echo ""
echo "⚠️  Note: Cloud SQL instances were NOT stopped to prevent data loss."
echo "   To stop Cloud SQL instances, uncomment the relevant section in this script."

