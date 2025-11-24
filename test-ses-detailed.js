const { SESClient, SendEmailCommand } = require('@aws-sdk/client-ses');
const { getSecrets } = require('./dist/config/secrets');

async function testSES() {
  try {
    const secrets = await getSecrets();
    
    console.log('Testing SES with credentials from Secret Manager...');
    console.log('Region:', 'us-west-2');
    console.log('From email:', 'admin@futurelink.zip');
    
    const client = new SESClient({
      region: 'us-west-2',
      credentials: {
        accessKeyId: secrets.AWS_ACCESS_KEY_ID,
        secretAccessKey: secrets.AWS_SECRET_ACCESS_KEY,
      },
    });

    const command = new SendEmailCommand({
      Source: 'admin@futurelink.zip',
      Destination: { ToAddresses: ['bcherrman@gmail.com'] },
      Message: {
        Subject: { Data: 'Test Email from JobMatch AI', Charset: 'UTF-8' },
        Body: { 
          Text: { 
            Data: 'This is a test email to verify SES configuration.', 
            Charset: 'UTF-8' 
          } 
        }
      }
    });

    const result = await client.send(command);
    console.log('SUCCESS: Email sent successfully!');
    console.log('Message ID:', result.MessageId);
  } catch (error) {
    console.log('ERROR:', error.message);
    console.log('Error code:', error.Code);
    console.log('Error type:', error.Type);
    if (error.$metadata) {
      console.log('HTTP Status:', error.$metadata.httpStatusCode);
    }
  }
}

testSES();
