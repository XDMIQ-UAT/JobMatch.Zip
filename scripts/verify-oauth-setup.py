#!/usr/bin/env python3
"""
Verify Google OAuth and Subscription Setup
Checks that all required environment variables are configured correctly.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
    """Check if environment variable is set."""
    value = os.getenv(name)
    if not value:
        if required:
            return False, f"❌ {name} is NOT set (REQUIRED)"
        else:
            return True, f"⚠️  {name} is NOT set (optional)"
    
    # Mask sensitive values
    if "SECRET" in name or "KEY" in name or "PASSWORD" in name:
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        return True, f"✅ {name} is set ({masked})"
    else:
        return True, f"✅ {name} is set ({value})"

def load_env_file():
    """Load .env file manually from multiple possible locations."""
    # Check multiple locations
    possible_locations = [
        Path(__file__).parent.parent / ".env",  # Root
        Path(__file__).parent.parent / "backend" / ".env",  # Backend directory
    ]
    
    loaded = False
    for env_file in possible_locations:
        if env_file.exists():
            # Load .env file manually
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            loaded = True
            return env_file
    
    return None if not loaded else possible_locations[0]

def main():
    print("=" * 80)
    print("Google OAuth & Subscription Setup Verification")
    print("=" * 80)
    print()
    
    # Load .env file if it exists (check multiple locations)
    env_file = load_env_file()
    if env_file:
        print(f"📄 Found and loaded .env file: {env_file}")
        print()
    else:
        root_env = Path(__file__).parent.parent / ".env"
        backend_env = Path(__file__).parent.parent / "backend" / ".env"
        print(f"⚠️  No .env file found in:")
        print(f"   - {root_env}")
        print(f"   - {backend_env}")
        print("   Make sure you've created a .env file with your configuration.")
        print()
    
    print("Checking Environment Variables:")
    print("-" * 80)
    
    # Google OAuth (check both naming conventions)
    print("\n🔐 Google OAuth Configuration:")
    google_oauth_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID") or os.getenv("GOOGLE_CLIENT_ID")
    google_oauth_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET") or os.getenv("GOOGLE_CLIENT_SECRET")
    
    if google_oauth_id:
        masked = google_oauth_id[:8] + "..." + google_oauth_id[-4:] if len(google_oauth_id) > 12 else "***"
        print(f"   ✅ GOOGLE_OAUTH_CLIENT_ID is set ({masked})")
        google_client_id_ok = True
    else:
        print(f"   ❌ GOOGLE_OAUTH_CLIENT_ID is NOT set (REQUIRED)")
        print(f"      Also checked: GOOGLE_CLIENT_ID")
        google_client_id_ok = False
    
    if google_oauth_secret:
        masked = google_oauth_secret[:8] + "..." + google_oauth_secret[-4:] if len(google_oauth_secret) > 12 else "***"
        print(f"   ✅ GOOGLE_OAUTH_CLIENT_SECRET is set ({masked})")
        google_client_secret_ok = True
    else:
        print(f"   ❌ GOOGLE_OAUTH_CLIENT_SECRET is NOT set (REQUIRED)")
        print(f"      Also checked: GOOGLE_CLIENT_SECRET")
        google_client_secret_ok = False
    
    # Stripe
    print("\n💳 Stripe Configuration:")
    stripe_secret_ok, stripe_secret_msg = check_env_var("STRIPE_SECRET_KEY", required=True)
    print(f"   {stripe_secret_msg}")
    
    stripe_webhook_ok, stripe_webhook_msg = check_env_var("STRIPE_WEBHOOK_SECRET", required=False)
    print(f"   {stripe_webhook_msg}")
    
    # URLs
    print("\n🌐 URL Configuration:")
    frontend_url_ok, frontend_url_msg = check_env_var("FRONTEND_URL", required=False)
    print(f"   {frontend_url_msg}")
    
    backend_url_ok, backend_url_msg = check_env_var("BACKEND_URL", required=False)
    print(f"   {backend_url_msg}")
    
    # Database (for anonymous identity)
    print("\n🗄️  Database Configuration:")
    db_url_ok, db_url_msg = check_env_var("DATABASE_URL", required=False)
    print(f"   {db_url_msg}")
    
    # Summary
    print()
    print("=" * 80)
    print("Summary:")
    print("-" * 80)
    
    all_required = (
        google_client_id_ok and
        google_client_secret_ok and
        stripe_secret_ok
    )
    
    if all_required:
        print("✅ All REQUIRED variables are configured!")
        print()
        print("Next Steps:")
        print("1. Test Google OAuth:")
        print("   Visit: http://localhost:8000/api/auth/google/login")
        print("   (or your BACKEND_URL + /api/auth/google/login)")
        print()
        print("2. Test Subscription:")
        print("   After authenticating, create checkout session:")
        print("   POST /api/subscription/create-checkout-session")
        print()
        print("3. Check subscription status:")
        print("   GET /api/subscription/status-by-anonymous-id/{anonymous_id}")
    else:
        print("❌ Some REQUIRED variables are missing!")
        print()
        print("Please set the following in your .env file:")
        if not google_client_id_ok:
            print("   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com")
        if not google_client_secret_ok:
            print("   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret")
        if not stripe_secret_ok:
            print("   STRIPE_SECRET_KEY=sk_test_... (or sk_live_... for production)")
        print()
        print("See docs/GOOGLE_OAUTH_SETUP.md for detailed setup instructions.")
    
    print()
    print("=" * 80)
    
    return 0 if all_required else 1

if __name__ == "__main__":
    sys.exit(main())

