#!/bin/bash
# Deploy JobMatch Platform to https://jobmatch.zip
# This script deploys both frontend and backend to Google Cloud Run with custom domain

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-us-central1}"
DOMAIN="${DOMAIN:-jobmatch.zip}"
FRONTEND_ONLY="${FRONTEND_ONLY:-false}"
BACKEND_ONLY="${BACKEND_ONLY:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Validate project ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No GCP project configured. Set GCP_PROJECT_ID or run: gcloud config set project PROJECT_ID${NC}"
    exit 1
fi

echo -e "${CYAN}🚀 Deploying JobMatch Platform to https://$DOMAIN${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check prerequisites
echo -e "${CYAN}📋 Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI found${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Authenticate
echo -e "${CYAN}🔐 Authenticating Docker...${NC}"
gcloud auth configure-docker --quiet

# Enable required APIs
echo -e "${CYAN}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID --quiet
gcloud services enable run.googleapis.com --project=$PROJECT_ID --quiet
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID --quiet
gcloud services enable servicenetworking.googleapis.com --project=$PROJECT_ID --quiet

# Deploy Backend
if [ "$FRONTEND_ONLY" != "true" ]; then
    echo -e "\n${CYAN}📦 Deploying Backend...${NC}"
    
    BACKEND_SERVICE="jobmatch-backend"
    BACKEND_IMAGE="gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest"
    
    # Build backend image
    echo -e "${CYAN}🔨 Building backend Docker image...${NC}"
    docker build -t $BACKEND_IMAGE -f Dockerfile.cloudrun .
    
    # Push image
    echo -e "${CYAN}📤 Pushing backend image...${NC}"
    docker push $BACKEND_IMAGE
    
    # Deploy to Cloud Run
    echo -e "${CYAN}🚀 Deploying backend to Cloud Run...${NC}"
    gcloud run deploy $BACKEND_SERVICE \
        --image $BACKEND_IMAGE \
        --platform managed \
        --region $REGION \
        --project $PROJECT_ID \
        --port 8080 \
        --memory 1Gi \
        --cpu 2 \
        --min-instances 1 \
        --max-instances 10 \
        --timeout 300 \
        --allow-unauthenticated \
        --set-env-vars "FRONTEND_URL=https://$DOMAIN" \
        --quiet
    
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --project $PROJECT_ID --format="value(status.url)")
    echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
fi

# Build Frontend
if [ "$BACKEND_ONLY" != "true" ]; then
    echo -e "\n${CYAN}📦 Building Frontend...${NC}"
    
    cd frontend
    
    # Install dependencies
    echo -e "${CYAN}📥 Installing frontend dependencies...${NC}"
    npm install
    
    # Build frontend
    echo -e "${CYAN}🔨 Building frontend...${NC}"
    export NODE_ENV="production"
    export VITE_API_URL="https://api.$DOMAIN"
    npm run build
    
    cd ..
    
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
fi

# Create Frontend Dockerfile if it doesn't exist
if [ ! -f "Dockerfile.frontend" ]; then
    echo -e "${CYAN}📝 Creating frontend Dockerfile...${NC}"
    cat > Dockerfile.frontend << 'EOF'
# Frontend Dockerfile for Cloud Run
FROM nginx:alpine

# Copy built frontend
COPY frontend/dist /usr/share/nginx/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
fi

# Create nginx config if it doesn't exist
if [ ! -f "frontend/nginx.conf" ]; then
    echo -e "${CYAN}📝 Creating nginx configuration...${NC}"
    mkdir -p frontend
    cat > frontend/nginx.conf << EOF
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # SPA routing - serve index.html for all routes
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass https://api.$DOMAIN;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
fi

# Deploy Frontend
if [ "$BACKEND_ONLY" != "true" ]; then
    echo -e "\n${CYAN}📦 Deploying Frontend...${NC}"
    
    FRONTEND_SERVICE="jobmatch-frontend"
    FRONTEND_IMAGE="gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest"
    
    # Build frontend image
    echo -e "${CYAN}🔨 Building frontend Docker image...${NC}"
    docker build -t $FRONTEND_IMAGE -f Dockerfile.frontend .
    
    # Push image
    echo -e "${CYAN}📤 Pushing frontend image...${NC}"
    docker push $FRONTEND_IMAGE
    
    # Deploy to Cloud Run
    echo -e "${CYAN}🚀 Deploying frontend to Cloud Run...${NC}"
    gcloud run deploy $FRONTEND_SERVICE \
        --image $FRONTEND_IMAGE \
        --platform managed \
        --region $REGION \
        --project $PROJECT_ID \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 1 \
        --max-instances 5 \
        --timeout 60 \
        --allow-unauthenticated \
        --quiet
    
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --project $PROJECT_ID --format="value(status.url)")
    echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"
fi

# Map Custom Domain
echo -e "\n${CYAN}🌐 Mapping custom domain...${NC}"
echo -e "${YELLOW}⚠️  You need to verify domain ownership first:${NC}"
echo "   1. Run: gcloud domains verify $DOMAIN"
echo "   2. Follow DNS verification instructions"
echo "   3. Then run domain mapping commands below"
echo ""

if [ "$BACKEND_ONLY" != "true" ]; then
    echo -e "${CYAN}Mapping frontend domain...${NC}"
    echo -e "${YELLOW}Run this command after domain verification:${NC}"
    echo "gcloud run domain-mappings create --service=$FRONTEND_SERVICE --domain=$DOMAIN --region=$REGION --project=$PROJECT_ID"
    echo ""
fi

echo -e "${CYAN}Mapping API subdomain...${NC}"
echo -e "${YELLOW}Run this command after domain verification:${NC}"
echo "gcloud run domain-mappings create --service=$BACKEND_SERVICE --domain=api.$DOMAIN --region=$REGION --project=$PROJECT_ID"
echo ""

# Summary
echo -e "${GREEN}\n✅ Deployment Complete!${NC}"
echo -e "${CYAN}\n📋 Next Steps:${NC}"
echo "   1. Verify domain ownership: gcloud domains verify $DOMAIN"
echo "   2. Map frontend domain: gcloud run domain-mappings create --service=$FRONTEND_SERVICE --domain=$DOMAIN --region=$REGION"
echo "   3. Map API domain: gcloud run domain-mappings create --service=$BACKEND_SERVICE --domain=api.$DOMAIN --region=$REGION"
echo "   4. Update DNS records as instructed by domain mapping commands"
echo "   5. Wait for SSL certificate provisioning (can take up to 15 minutes)"
echo ""
echo -e "${GREEN}🎉 Your app will be available at:${NC}"
if [ "$BACKEND_ONLY" != "true" ]; then
    echo -e "   Frontend: ${GREEN}https://$DOMAIN${NC}"
fi
if [ "$FRONTEND_ONLY" != "true" ]; then
    echo -e "   Backend API: ${GREEN}https://api.$DOMAIN${NC}"
fi

