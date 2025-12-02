// Vercel serverless function handler
// This wraps the Express app for Vercel's serverless function runtime

// Import the Express app from the built backend
// The compiled JS uses CommonJS exports, so we use .app
const backendApp = require('../backend/dist/index.js');

// Get the Express app (it's exported as .app in CommonJS)
const app = backendApp.app || backendApp.default || backendApp;

// Vercel serverless function handler
// Express app can be exported directly
module.exports = app;

