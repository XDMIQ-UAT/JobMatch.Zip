"""Check the status of a Twilio call"""
import json
import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client

# Get credentials
auth = HTTPBasicAuth('admin', 'XRi6TgSrwfeuK8taYzhknoJc')
r = requests.get('https://mykeys.zip/api/secrets/twilio-credentials', auth=auth, timeout=10)
data = r.json()
creds = json.loads(data['value']) if isinstance(data.get('value'), str) else data.get('value')

# Initialize Twilio client
client = Client(creds['account_sid'], creds['auth_token'])

# Check call status - update this SID to check different calls
call_sid = 'CA4e606fc6cf3a63559214e97fe4d31bcc'  # New call
call = client.calls(call_sid).fetch()

print(f"Call SID: {call.sid}")
print(f"Status: {call.status}")
print(f"From: {getattr(call, 'from_', getattr(call, 'from', 'N/A'))}")
print(f"To: {call.to}")
print(f"Duration: {call.duration} seconds" if call.duration else "Duration: N/A")
print(f"Price: ${call.price}" if call.price else "Price: N/A")
if hasattr(call, 'error_code') and call.error_code:
    print(f"Error Code: {call.error_code}")
if hasattr(call, 'error_message') and call.error_message:
    print(f"Error Message: {call.error_message}")
print(f"\nNote: Status '{call.status}' means the call is currently ringing or in progress.")
print("If you didn't answer, it may have gone to voicemail or timed out.")

