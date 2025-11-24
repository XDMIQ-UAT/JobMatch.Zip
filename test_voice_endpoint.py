"""
Test script for Twilio voice endpoints.
Run this to verify endpoints work before configuring Twilio.
"""
import requests
from xml.etree import ElementTree as ET

BASE_URL = "http://localhost:8000"  # Change to https://jobmatch.zip in production


def test_health_check():
    """Test voice health endpoint."""
    print("\n=== Testing Voice Health Check ===")
    response = requests.get(f"{BASE_URL}/api/voice/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_incoming_call():
    """Test incoming call endpoint."""
    print("\n=== Testing Incoming Call ===")
    data = {
        "From": "+15551234567",
        "To": "+15559876543",
        "CallSid": "CA1234567890abcdef",
        "CallStatus": "ringing"
    }
    response = requests.post(f"{BASE_URL}/api/voice/incoming", data=data)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers['content-type']}")
    
    # Parse TwiML
    twiml = response.text
    print(f"\nTwiML Response:\n{twiml}")
    
    # Validate XML
    try:
        root = ET.fromstring(twiml)
        assert root.tag == "Response"
        gather = root.find("Gather")
        assert gather is not None
        assert gather.get("action") == "/api/voice/menu"
        say = gather.find("Say")
        assert say is not None
        print("\n✓ TwiML structure valid")
        print(f"✓ Welcome message: {say.text[:50]}...")
    except Exception as e:
        print(f"✗ XML validation failed: {e}")
        raise
    
    assert response.status_code == 200
    print("✓ Incoming call endpoint passed")


def test_menu_selection_1():
    """Test menu option 1 (about services)."""
    print("\n=== Testing Menu Option 1 ===")
    data = {
        "Digits": "1",
        "CallSid": "CA1234567890abcdef"
    }
    response = requests.post(f"{BASE_URL}/api/voice/menu", data=data)
    print(f"Status: {response.status_code}")
    
    twiml = response.text
    print(f"\nTwiML Response:\n{twiml}")
    
    root = ET.fromstring(twiml)
    say = root.find("Say")
    assert say is not None
    assert "Job Match helps" in say.text
    print("✓ Menu option 1 passed")


def test_menu_selection_2():
    """Test menu option 2 (AI assistant)."""
    print("\n=== Testing Menu Option 2 ===")
    data = {
        "Digits": "2",
        "CallSid": "CA1234567890abcdef"
    }
    response = requests.post(f"{BASE_URL}/api/voice/menu", data=data)
    print(f"Status: {response.status_code}")
    
    twiml = response.text
    root = ET.fromstring(twiml)
    say = root.find("Say")
    assert "A I assistant" in say.text
    print("✓ Menu option 2 passed")


def test_menu_selection_3():
    """Test menu option 3 (callback)."""
    print("\n=== Testing Menu Option 3 ===")
    data = {
        "Digits": "3",
        "CallSid": "CA1234567890abcdef"
    }
    response = requests.post(f"{BASE_URL}/api/voice/menu", data=data)
    print(f"Status: {response.status_code}")
    
    twiml = response.text
    root = ET.fromstring(twiml)
    say = root.find("Say")
    assert "schedule a callback" in say.text
    print("✓ Menu option 3 passed")


def test_menu_selection_9():
    """Test menu option 9 (end call)."""
    print("\n=== Testing Menu Option 9 ===")
    data = {
        "Digits": "9",
        "CallSid": "CA1234567890abcdef"
    }
    response = requests.post(f"{BASE_URL}/api/voice/menu", data=data)
    print(f"Status: {response.status_code}")
    
    twiml = response.text
    root = ET.fromstring(twiml)
    say = root.find("Say")
    assert "Thank you for calling" in say.text
    print("✓ Menu option 9 passed")


def test_menu_invalid():
    """Test invalid menu selection."""
    print("\n=== Testing Invalid Menu Selection ===")
    data = {
        "Digits": "7",
        "CallSid": "CA1234567890abcdef"
    }
    response = requests.post(f"{BASE_URL}/api/voice/menu", data=data)
    print(f"Status: {response.status_code}")
    
    twiml = response.text
    root = ET.fromstring(twiml)
    say = root.find("Say")
    assert "Invalid selection" in say.text
    print("✓ Invalid menu handling passed")


def test_status_callback():
    """Test status callback endpoint."""
    print("\n=== Testing Status Callback ===")
    data = {
        "CallSid": "CA1234567890abcdef",
        "CallStatus": "completed",
        "CallDuration": "45"
    }
    response = requests.post(f"{BASE_URL}/api/voice/status", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "received"
    print("✓ Status callback passed")


def run_all_tests():
    """Run all voice endpoint tests."""
    print("=" * 60)
    print("TWILIO VOICE ENDPOINT TESTS")
    print("=" * 60)
    
    try:
        test_health_check()
        test_incoming_call()
        test_menu_selection_1()
        test_menu_selection_2()
        test_menu_selection_3()
        test_menu_selection_9()
        test_menu_invalid()
        test_status_callback()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Deploy to production (jobmatch.zip)")
        print("2. Configure Twilio webhook: https://jobmatch.zip/api/voice/incoming")
        print("3. Test with real phone call")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR")
        print(f"Make sure the backend is running at {BASE_URL}")
        print("Run: docker-compose up backend")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
