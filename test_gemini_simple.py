#!/usr/bin/env python3
"""
Simple Gemini Test - Test your API with a basic question
"""

import google.generativeai as genai

def test_gemini():
    """Test Gemini with your API key"""
    
    # Your API key
    API_KEY = "AIzaSyDM5YCtLwRUQgTTM8CBiCWtDY9Mr8Dr95M"
    
    print("🚀 Testing Google Gemini API")
    print("=" * 40)
    
    try:
        # Configure Gemini
        genai.configure(api_key=API_KEY)
        
        # Use the Flash model (higher rate limits)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test
        print("🤖 Asking: 'What are 3 steps to test a WiFi amplifier?'")
        
        response = model.generate_content(
            "What are 3 main steps to test a 2.4GHz WiFi power amplifier? Be concise."
        )
        
        print("\n✅ Gemini Response:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        print("\n🎯 Gemini API is working! Now your TestPilot can use AI.")
        
    except Exception as e:
        if "429" in str(e):
            print("⏳ Rate limit hit. Try again in a few minutes.")
            print("💡 Gemini Flash has higher limits than Pro - we've switched to Flash.")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini()