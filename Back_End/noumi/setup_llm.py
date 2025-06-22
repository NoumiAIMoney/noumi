#!/usr/bin/env python3
"""
Setup script for Noumi AI LLM configuration
Helps set up API keys for real AI calls instead of demo mode.
"""

import os
import sys


def setup_google_gemini():
    """Setup Google Gemini API (Free tier available)."""
    print("🤖 Setting up Google Gemini API")
    print("=" * 50)
    print("1. Go to: https://ai.google.dev/gemini-api/docs/api-key")
    print("2. Click 'Get API key' and create a new key")
    print("3. Copy the API key and paste it here")
    print()
    
    api_key = input("Enter your Google Gemini API key: ").strip()
    
    if api_key:
        # Set environment variable for current session
        os.environ['GOOGLE_API_KEY'] = api_key
        
        # Create .env file for persistent storage
        with open('.env', 'w') as f:
            f.write(f"GOOGLE_API_KEY={api_key}\n")
        
        print("✅ Google Gemini API key configured!")
        print("📁 Saved to .env file for future use")
        return True
    else:
        print("❌ No API key provided")
        return False


def setup_openai():
    """Setup OpenAI API (Paid service)."""
    print("🤖 Setting up OpenAI API")
    print("=" * 50)
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the API key and paste it here")
    print("⚠️  Note: OpenAI is a paid service")
    print()
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if api_key:
        # Set environment variable for current session
        os.environ['OPENAI_API_KEY'] = api_key
        
        # Create/append to .env file
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
        
        if 'OPENAI_API_KEY' not in env_content:
            with open('.env', 'a') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
        
        print("✅ OpenAI API key configured!")
        print("📁 Saved to .env file for future use")
        return True
    else:
        print("❌ No API key provided")
        return False


def load_env_file():
    """Load environment variables from .env file."""
    if os.path.exists('.env'):
        print("📁 Loading existing .env configuration...")
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        return True
    return False


def test_llm_connection():
    """Test if LLM connection works."""
    try:
        # Import and test the LLM client
        sys.path.append('noumi_agents/utils')
        from llm_client import NoumiLLMClient
        
        print("\n🧪 Testing LLM connection...")
        
        # Try Google Gemini first
        if os.getenv('GOOGLE_API_KEY'):
            client = NoumiLLMClient(provider="google")
            if client.client:
                print("✅ Google Gemini connected successfully!")
                return True
        
        # Try OpenAI as fallback
        if os.getenv('OPENAI_API_KEY'):
            client = NoumiLLMClient(provider="openai")
            if client.client:
                print("✅ OpenAI connected successfully!")
                return True
        
        print("❌ No working LLM connection found")
        return False
        
    except Exception as e:
        print(f"❌ Error testing LLM connection: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Noumi AI LLM Setup")
    print("=" * 60)
    msg = "This script will help you set up real AI calls instead of demo mode."
    print(msg)
    print()
    
    # Load existing configuration
    load_env_file()
    
    # Check if already configured
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    if google_key or openai_key:
        print("🔍 Found existing API key configuration")
        if test_llm_connection():
            print("\n🎉 LLM is already configured and working!")
            print("Your API examples will now use real AI calls.")
            return
        else:
            msg = "⚠️  Existing configuration not working, please reconfigure."
            print(msg)
    
    print("\nChoose your preferred LLM provider:")
    print("1. Google Gemini (Recommended - Free tier available)")
    print("2. OpenAI (Paid service)")
    print("3. Skip setup (continue with demo mode)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        if setup_google_gemini():
            test_llm_connection()
    elif choice == "2":
        if setup_openai():
            test_llm_connection()
    elif choice == "3":
        print("⏭️  Skipping LLM setup - will continue in demo mode")
    else:
        print("❌ Invalid choice")
        return
    
    print("\n" + "=" * 60)
    print("🔧 Next Steps:")
    print("1. Restart your API server: python noumi_api.py")
    print("2. Test with real AI: python api_examples.py")
    print("3. Your .env file will be used automatically")
    print("=" * 60)


if __name__ == "__main__":
    main() 