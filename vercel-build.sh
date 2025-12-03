#!/bin/bash
set -e

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Build backend
cd backend
npm install
npx prisma generate
npm run build
cd ..

# Copy backend build to api directory
cp -r backend/dist api/backend-dist
cp backend/dist/index.js api/backend-index.js

# Copy Prisma schema and generate client in api directory
mkdir -p api/prisma
cp backend/prisma/schema.prisma api/prisma/schema.prisma

# Install @prisma/client and prisma CLI in api if not already installed
cd api
if [ ! -d "node_modules/@prisma" ]; then
  npm install @prisma/client@^5.7.1 prisma@^5.7.1 --save
fi

# Generate Prisma client in api directory (this creates node_modules/.prisma/client)
npx prisma generate --schema=./prisma/schema.prisma

# Verify Prisma client was generated
if [ ! -d "node_modules/.prisma/client" ]; then
  echo "⚠️ WARNING: Prisma client not found in api/node_modules/.prisma/client"
  echo "Attempting to copy from backend..."
  mkdir -p node_modules/.prisma
  cp -r ../backend/node_modules/.prisma/* node_modules/.prisma/ 2>/dev/null || true
else
  echo "✅ Prisma client generated successfully in api/node_modules/.prisma/client"
fi
cd ..

echo "✅ Build complete"

