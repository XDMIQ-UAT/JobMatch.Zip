FROM node:18-alpine

WORKDIR /app

# Copy package files first for caching
COPY package*.json ./
RUN if [ -f package.json ]; then npm install; fi

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Command is specified in docker-compose.yml
CMD ["npm", "run", "dev"]
