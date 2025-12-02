// Simple test API function to verify Vercel detects api/ folder
module.exports = (req, res) => {
  res.json({ 
    message: 'Test API function works!',
    path: req.url,
    method: req.method
  });
};

