#!/usr/bin/env python3
"""
Test AI API Connection
Quick test to verify your API keys are working
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_ai_connection():
    """Test AI API connection with your keys"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔑 Testing AI API Connection")
    print("=" * 40)
    
    # Check for API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"Google Gemini API Key: {'✅ Found' if google_key and google_key != 'your_google_api_key_here' else '❌ Not configured'}")
    print(f"Anthropic API Key: {'✅ Found' if anthropic_key and anthropic_key != 'your_claude_api_key_here' else '❌ Not configured'}")
    print(f"OpenAI API Key: {'✅ Found' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ Not configured'}")
    
    if not google_key and not anthropic_key and not openai_key:
        print("\n⚠️  No API keys configured!")
        print("Edit the .env file and add your API keys.")
        return
    
    # Test Google Gemini if available
    if google_key and google_key != 'your_google_api_key_here':
        print(f"\n🤖 Testing Google Gemini...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                "Generate a brief test plan for testing a 2.4GHz WiFi amplifier. Just list 3 main steps."
            )
            
            print("✅ Google Gemini API working!")
            print(f"Response: {response.text[:200]}...")
            
        except Exception as e:
            print(f"❌ Gemini API failed: {e}")
    
    # Test Anthropic if available
    if anthropic_key and anthropic_key != 'your_claude_api_key_here':
        print(f"\n🧠 Testing Anthropic Claude...")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[{
                    "role": "user", 
                    "content": "Generate a brief test plan for testing a 2.4GHz WiFi amplifier. Just list 3 main steps."
                }]
            )
            
            print("✅ Anthropic Claude API working!")
            print(f"Response: {message.content[0].text[:200]}...")
            
        except Exception as e:
            print(f"❌ Anthropic API failed: {e}")
    
    # Test OpenAI if available
    if openai_key and openai_key != 'your_openai_api_key_here':
        print(f"\n🤖 Testing OpenAI GPT...")
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": "Generate a brief test plan for testing a 2.4GHz WiFi amplifier. Just list 3 main steps."
                }]
            )
            
            print("✅ OpenAI GPT API working!")
            print(f"Response: {response.choices[0].message.content[:200]}...")
            
        except Exception as e:
            print(f"❌ OpenAI API failed: {e}")
    
    print(f"\n🎯 Next Steps:")
    print("1. Open http://localhost:3000")
    print("2. Try the chat interface with: 'Test a WiFi amplifier'")
    print("3. Click 'Start Recording' for real-time plots")

if __name__ == "__main__":
    asyncio.run(test_ai_connection())