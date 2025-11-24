"""
Test SES Email Configuration and Sending
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from config import settings
from auth.email_provider import create_email_manager

async def test_ses_config():
    """Test SES configuration and email sending."""
    print("=" * 60)
    print("Testing SES Email Configuration")
    print("=" * 60)
    print()
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"   EMAIL_PROVIDER_MODE: {getattr(settings, 'EMAIL_PROVIDER_MODE', 'not set')}")
    print(f"   AWS_ACCESS_KEY_ID: {getattr(settings, 'AWS_ACCESS_KEY_ID', '')[:10]}..." if getattr(settings, 'AWS_ACCESS_KEY_ID', '') else "   AWS_ACCESS_KEY_ID: NOT SET")
    print(f"   AWS_SECRET_ACCESS_KEY: {'SET' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', '') else 'NOT SET'}")
    print(f"   SES_REGION: {getattr(settings, 'SES_REGION', 'not set')}")
    print(f"   SES_FROM_EMAIL: {getattr(settings, 'SES_FROM_EMAIL', 'not set')}")
    print()
    
    # Create email manager
    print("🔧 Initializing Email Manager...")
    try:
        email_manager = create_email_manager()
        print(f"   Provider Mode: {email_manager.provider_mode}")
        print(f"   From Email: {email_manager.from_email}")
        print(f"   SES Client: {'✅ Initialized' if email_manager.ses_client else '❌ Not initialized'}")
        print()
        
        if not email_manager.ses_client:
            print("❌ SES client not initialized!")
            print("   Possible reasons:")
            print("   - EMAIL_PROVIDER_MODE is not 'ses'")
            print("   - AWS credentials not set")
            print("   - Failed to create SES client")
            return False
        
        # Test SES connection
        print("🔌 Testing SES Connection...")
        try:
            quota = email_manager.ses_client.get_send_quota()
            print(f"   ✅ Connection successful!")
            print(f"   Max 24h Send: {quota.get('Max24HourSend', 'N/A')}")
            print(f"   Sent Last 24h: {quota.get('SentLast24Hours', 'N/A')}")
            print(f"   Max Send Rate: {quota.get('MaxSendRate', 'N/A')}")
            print()
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
        
        # Check verified identities
        print("📧 Checking Verified Identities...")
        try:
            identities = email_manager.ses_client.list_verified_email_addresses()
            verified_emails = identities.get('VerifiedEmailAddresses', [])
            print(f"   Verified Emails: {len(verified_emails)}")
            for email in verified_emails[:5]:  # Show first 5
                print(f"     - {email}")
            if len(verified_emails) > 5:
                print(f"     ... and {len(verified_emails) - 5} more")
            print()
            
            # Check if sender email is verified
            sender_email = email_manager.from_email
            if sender_email not in verified_emails:
                print(f"   ⚠️  WARNING: Sender email '{sender_email}' is NOT verified!")
                print(f"      You need to verify this email in AWS SES console.")
                print()
        except Exception as e:
            print(f"   ⚠️  Could not check verified identities: {e}")
            print()
        
        # Test email sending (to a test email)
        print("📨 Testing Email Send...")
        test_email = input("   Enter test email address (or press Enter to skip): ").strip()
        
        if not test_email:
            print("   Skipping email send test")
            return True
        
        print(f"   Sending test email to: {test_email}")
        result = await email_manager.send_verification_email(
            email=test_email,
            code="123456"
        )
        
        if result.get("success"):
            print(f"   ✅ Email sent successfully!")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
            print(f"   Provider: {result.get('provider', 'N/A')}")
        else:
            print(f"   ❌ Email send failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ses_config())
    sys.exit(0 if success else 1)

