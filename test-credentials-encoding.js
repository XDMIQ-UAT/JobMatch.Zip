const { getSecrets } = require('./dist/config/secrets');

getSecrets().then(secrets => {
  console.log('AWS_ACCESS_KEY_ID:');
  console.log('Length:', secrets.AWS_ACCESS_KEY_ID?.length);
  console.log('Raw bytes:', Buffer.from(secrets.AWS_ACCESS_KEY_ID || '', 'utf8').toString('hex'));
  console.log('String:', JSON.stringify(secrets.AWS_ACCESS_KEY_ID));
  
  console.log('\nAWS_SECRET_ACCESS_KEY:');
  console.log('Length:', secrets.AWS_SECRET_ACCESS_KEY?.length);
  console.log('Raw bytes:', Buffer.from(secrets.AWS_SECRET_ACCESS_KEY || '', 'utf8').toString('hex'));
  console.log('String:', JSON.stringify(secrets.AWS_SECRET_ACCESS_KEY));
}).catch(err => console.error('Error:', err.message));
