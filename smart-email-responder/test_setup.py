#!/usr/bin/env python3
"""
Test script to verify setup before running the main agent
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_key():
    """Test if OpenAI API key is working"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not set in .env file")
        print("Please edit .env file and add your actual API key")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API key works!'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API key error: {e}")
        return False

def test_credentials_file():
    """Test if credentials.json exists"""
    if os.path.exists('credentials.json'):
        print("✅ credentials.json file found")
        return True
    else:
        print("❌ credentials.json file not found")
        print("Please download it from Google Cloud Console")
        return False

def main():
    print("🧪 Testing setup for Smart Email Responder...\n")
    
    openai_ok = test_openai_key()
    credentials_ok = test_credentials_file()
    
    print(f"\n📋 Setup Status:")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    print(f"Google Credentials: {'✅' if credentials_ok else '❌'}")
    
    if openai_ok and credentials_ok:
        print("\n🎉 All setup complete! You can run the smart email responder.")
        print("Run: python smart_email_responder.py")
    else:
        print("\n⚠️  Please complete the missing setup steps above.")

if __name__ == "__main__":
    main()