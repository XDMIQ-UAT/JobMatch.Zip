"""Quick test script for OpenRouter chat integration."""
import sys
sys.path.insert(0, "E:\\JobFinder")

from backend.llm import get_llm_client

def test_chat():
    print("Initializing LLM client...")
    llm = get_llm_client()
    
    print(f"✓ Provider: {llm.provider}")
    print(f"✓ Model: {llm.model}")
    print()
    
    print("Testing chat with a simple greeting...")
    messages = [
        {"role": "system", "content": "You are a helpful job matching assistant."},
        {"role": "user", "content": "Hello! What authentication methods do you support?"}
    ]
    
    try:
        response = llm.chat(messages=messages, temperature=0.7, max_tokens=500)
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(response)
        print("="*60)
        print("\n✓ Test successful!")
        return True
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chat()
    sys.exit(0 if success else 1)
