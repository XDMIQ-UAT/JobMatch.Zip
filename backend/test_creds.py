import sys
sys.path.insert(0, '..')
import json
from config import settings

creds = getattr(settings, 'GOOGLE_SEARCH_CONSOLE_CREDENTIALS', '')
print(f'Raw length: {len(creds)}')
print(f'First 100: {creds[:100]}')

# Remove surrounding quotes
if creds.startswith("'") and creds.endswith("'"):
    creds = creds[1:-1]
elif creds.startswith('"') and creds.endswith('"'):
    creds = creds[1:-1]

# Unescape
creds = creds.replace('\\"', '"')

try:
    info = json.loads(creds)
    print('✅ JSON parsed successfully')
    print(f'Project: {info.get("project_id")}')
    print(f'Email: {info.get("client_email")}')
except Exception as e:
    print(f'❌ Error: {e}')
    print(f'First 200 chars: {creds[:200]}')

