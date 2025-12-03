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

# Install @prisma/client in api if not already installed
cd api
if [ ! -d "node_modules/@prisma" ]; then
  npm install @prisma/client@^5.7.1 --save
fi

# Generate Prisma client in api directory
npx prisma generate --schema=./prisma/schema.prisma
cd ..

# Also copy the generated client from backend as backup
mkdir -p api/node_modules/.prisma
cp -r backend/node_modules/.prisma/* api/node_modules/.prisma/ 2>/dev/null || true

echo "✅ Build complete"

