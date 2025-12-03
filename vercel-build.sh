#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install || { echo "❌ Frontend npm install failed"; exit 1; }
npm run build || { echo "❌ Frontend build failed"; exit 1; }
cd ..
echo "✅ Frontend build complete"

# Build backend
echo "📦 Building backend..."
cd backend
npm install || { echo "❌ Backend npm install failed"; exit 1; }
npx prisma generate || { echo "❌ Prisma generate failed"; exit 1; }
npm run build || { echo "❌ Backend build failed"; exit 1; }
cd ..
echo "✅ Backend build complete"

# Verify backend/dist exists
if [ ! -d "backend/dist" ]; then
  echo "❌ ERROR: backend/dist not found after build!"
  exit 1
fi

# Copy backend build to api directory
echo "📋 Copying backend build to api directory..."
mkdir -p api/backend-dist
cp -r backend/dist/* api/backend-dist/ || { echo "❌ Failed to copy backend/dist"; exit 1; }
cp backend/dist/index.js api/backend-index.js || { echo "⚠️ WARNING: Failed to copy backend-index.js (may not be critical)"; }
echo "✅ Backend files copied"

# Copy Prisma schema and generate client in api directory
echo "🔧 Setting up Prisma in api directory..."
mkdir -p api/prisma
cp backend/prisma/schema.prisma api/prisma/schema.prisma || { echo "❌ Failed to copy Prisma schema"; exit 1; }

# Install @prisma/client and prisma CLI in api if not already installed
cd api
if [ ! -d "node_modules/@prisma" ]; then
  echo "📥 Installing Prisma in api directory..."
  npm install @prisma/client@^5.7.1 prisma@^5.7.1 --save || { echo "⚠️ WARNING: Prisma install failed, but continuing..."; }
fi

# Generate Prisma client in api directory (this creates node_modules/.prisma/client)
echo "🔨 Generating Prisma client in api directory..."
npx prisma generate --schema=./prisma/schema.prisma || {
  echo "⚠️ WARNING: Prisma generate in api failed, attempting to copy from backend..."
  mkdir -p node_modules/.prisma
  cp -r ../backend/node_modules/.prisma/* node_modules/.prisma/ 2>/dev/null || {
    echo "⚠️ WARNING: Could not copy Prisma client from backend"
  }
}

# Verify Prisma client was generated
if [ ! -d "node_modules/.prisma/client" ]; then
  echo "⚠️ WARNING: Prisma client not found in api/node_modules/.prisma/client"
  echo "This may cause runtime issues, but build will continue..."
else
  echo "✅ Prisma client generated successfully in api/node_modules/.prisma/client"
fi
cd ..

echo "✅ Build complete"

