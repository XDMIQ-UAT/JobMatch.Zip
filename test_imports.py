#!/usr/bin/env python3
import sys
import traceback

modules_to_test = [
    'config',
    'database.connection',
    'database.models',
    'auth.session_manager',
    'auth.social_auth',
    'auth.email_provider',
    'assessment.capability_assessment',
    'ai.articulation_assistant',
    'security.security_headers',
    'security.rate_limiter',
    'api.auth',
    'api.assessment',
    'api.matching',
    'api.articulation',
    'api.forums',
    'api.referrals',
    'api.xdmiq',
    'api.social_auth',
    'api.gcp_cli',
    'api.marketplace',
    'api.canvas',
    'api.security',
    'api.conversations',
    'api.seo',
    'api.users',
    'api.chat',
    'api.voice',
    'api.sms',
    'api.subscription',
]

print("Testing imports...")
failed = []
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {module}")
    except Exception as e:
        print(f"✗ {module}: {e}")
        failed.append((module, str(e)))
        
print(f"\n{len(failed)} failures out of {len(modules_to_test)} modules")
if failed:
    print("\nFirst failure details:")
    print(f"Module: {failed[0][0]}")
    print(f"Error: {failed[0][1]}")
