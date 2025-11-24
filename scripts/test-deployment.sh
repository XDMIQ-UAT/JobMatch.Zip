#!/bin/bash
# Test Deployment Endpoints

set -e

VM_IP="${VM_IP:-$1}"

if [ -z "$VM_IP" ]; then
    echo "❌ Usage: $0 <VM_IP_ADDRESS>"
    echo "   Or set VM_IP environment variable"
    exit 1
fi

echo "🧪 Testing deployment at $VM_IP"
echo ""

# Test endpoints
ENDPOINTS=(
    "/health"
    "/api/health"
    "/api/docs"
    "/canvas"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Testing: http://$VM_IP$endpoint"
    if curl -f -s -o /dev/null -w "  ✅ Status: %{http_code}\n" "http://$VM_IP$endpoint"; then
        echo "  ✅ Success"
    else
        echo "  ❌ Failed"
    fi
    echo ""
done

# Test API endpoints
echo "Testing API endpoints..."
echo ""

# Health check
echo "1. Health Check:"
curl -s "http://$VM_IP/api/health" | jq '.' || curl -s "http://$VM_IP/api/health"
echo ""
echo ""

# Test canvas info
echo "2. Canvas Info:"
curl -s "http://$VM_IP/api/canvas/info" | jq '.' || curl -s "http://$VM_IP/api/canvas/info"
echo ""
echo ""

echo "✅ Testing complete!"
echo ""
echo "📋 UAT Checklist:"
echo "  [ ] Frontend loads: http://$VM_IP"
echo "  [ ] Universal Canvas works: http://$VM_IP/canvas"
echo "  [ ] API docs accessible: http://$VM_IP/api/docs"
echo "  [ ] Health endpoint responds: http://$VM_IP/health"
echo "  [ ] Backend API responds: http://$VM_IP/api/health"

