const { getSecrets } = require('./dist/config/secrets');

getSecrets().then(secrets => {
  console.log('AWS_ACCESS_KEY_ID length:', secrets.AWS_ACCESS_KEY_ID?.length || 'undefined');
  console.log('AWS_SECRET_ACCESS_KEY length:', secrets.AWS_SECRET_ACCESS_KEY?.length || 'undefined');
  console.log('AWS_ACCESS_KEY_ID starts with:', secrets.AWS_ACCESS_KEY_ID?.substring(0, 10) || 'undefined');
  console.log('AWS_SECRET_ACCESS_KEY starts with:', secrets.AWS_SECRET_ACCESS_KEY?.substring(0, 10) || 'undefined');
}).catch(err => console.error('Error:', err.message));
