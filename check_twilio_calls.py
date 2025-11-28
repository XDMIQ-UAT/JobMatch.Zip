"""Check recent Twilio calls and account status"""
import json
import sys
import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get credentials
auth = HTTPBasicAuth('admin', 'XRi6TgSrwfeuK8taYzhknoJc')
r = requests.get('https://mykeys.zip/api/secrets/twilio-credentials', auth=auth, timeout=10)
data = r.json()
creds = json.loads(data['value']) if isinstance(data.get('value'), str) else data.get('value')

# Initialize Twilio client
client = Client(creds['account_sid'], creds['auth_token'])

print("=" * 60)
print("Twilio Account & Call Status")
print("=" * 60)

# Check account status
account = client.api.accounts(creds['account_sid']).fetch()
print(f"\nAccount Status: {account.status}")
print(f"Account Type: {account.type}")

# Check phone numbers
print(f"\nPhone Numbers:")
incoming_phone_numbers = client.incoming_phone_numbers.list(limit=10)
for number in incoming_phone_numbers:
    print(f"  - {number.phone_number} (SID: {number.sid[:20]}...)")

# Check recent calls (last 5)
print(f"\nRecent Calls (last 5):")
recent_calls = client.calls.list(limit=5)
for call in recent_calls:
    status_icon = "[OK]" if call.status == "completed" else "[FAIL]" if call.status == "failed" else "[...]"
    from_num = getattr(call, 'from_', getattr(call, 'from', 'N/A'))
    print(f"  {status_icon} {call.sid[:20]}... | {call.status:12} | From: {from_num} | To: {call.to} | Duration: {call.duration or 0}s")
    if hasattr(call, 'error_code') and call.error_code:
        print(f"      Error: {call.error_code} - {getattr(call, 'error_message', 'N/A')}")

# Check specific call
print(f"\nSpecific Call Status:")
call_sid = 'CA9e05fb33b08432bb0a9a50c6d181fb49'
try:
    call = client.calls(call_sid).fetch()
    print(f"  SID: {call.sid}")
    print(f"  Status: {call.status}")
    print(f"  From: {getattr(call, 'from_', getattr(call, 'from', 'N/A'))}")
    print(f"  To: {call.to}")
    print(f"  Start Time: {call.start_time}")
    print(f"  Duration: {call.duration} seconds" if call.duration else "  Duration: Still in progress")
    if hasattr(call, 'error_code') and call.error_code:
        print(f"  Error Code: {call.error_code}")
        print(f"  Error Message: {getattr(call, 'error_message', 'N/A')}")
except Exception as e:
    print(f"  Error fetching call: {e}")

