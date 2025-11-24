"""Test OpenRouter with JobMatch-specific prompts."""
import sys
sys.path.insert(0, "E:\\JobFinder")

from backend.llm import get_llm_client

def test_jobmatch_chat():
    """Test with JobMatch authentication scenario."""
    llm = get_llm_client()
    
    print(f"Provider: {llm.provider} | Model: {llm.model}\n")
    
    # Simulate the authentication conversation
    messages = [
        {
            "role": "system",
            "content": """You are a helpful job matching assistant for JobMatch - a platform for LLC owners who work with AI.
            
Your role is to:
- Help users authenticate (email, SMS, or OAuth providers)
- Guide them through job matching
- Remember conversation context
- Be friendly and professional

The platform supports these authentication methods:
- Email (magic link)
- SMS/VoIP (verification code)
- LinkedIn, Microsoft, Facebook, Google, Apple (OAuth)"""
        },
        {
            "role": "assistant",
            "content": "Hi there! 👋 Welcome to JobMatch - the first job matching platform for LLC owners who work with AI. I'm here to help you discover opportunities that match your capabilities.\n\nTo get started, let's set up your anonymous identity. Your privacy is protected - we'll never reveal your real identity. Which authentication method would you prefer?"
        },
        {
            "role": "user",
            "content": "I'd like to use email authentication"
        },
        {
            "role": "assistant",
            "content": "📧 **Email Authentication**\n\nGreat choice! I'll send you a magic link - no password needed.\n\n**Please enter your email address in the chat below:**"
        },
        {
            "role": "user",
            "content": "test@example.com"
        },
        {
            "role": "assistant", 
            "content": "✅ **Magic link sent!**\n\nI've sent a magic link to **test@example.com**.\n\n**Next steps:**\n1. Check your email inbox (and spam folder just in case)\n2. Click the link in the email\n3. You'll be redirected back here, authenticated and ready to go!\n\nThe link is valid for 24 hours."
        },
        {
            "role": "user",
            "content": "What authentication methods do you support again?"
        }
    ]
    
    print("Testing conversational intelligence...")
    print("(Should remember we just discussed email auth)\n")
    print("="*70)
    
    response = llm.chat(messages=messages, temperature=0.7, max_tokens=300)
    
    print("RESPONSE:")
    print("="*70)
    print(response)
    print("="*70)
    print("\n✓ Test complete!")
    print("\nKey observation: Did it remember we just used email authentication?")

if __name__ == "__main__":
    test_jobmatch_chat()
