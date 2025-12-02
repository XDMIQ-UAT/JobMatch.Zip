// Vercel serverless function handler
// This wraps the Express app for Vercel's serverless function runtime
const path = require('path');

// Import the Express app from the built backend
// Note: The backend exports both app and default, so we can use either
let app;
try {
  // Try default export first (for Vercel compatibility)
  app = require('../backend/dist/index.js').default || require('../backend/dist/index.js').app;
} catch (error) {
  // Fallback to named export
  app = require('../backend/dist/index.js').app;
}

// Export for Vercel serverless function
module.exports = app;

