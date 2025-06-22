#!/usr/bin/env python3
"""
TestPilot System Status Check
Quick check of all services and components
"""

import requests
import subprocess
import os

def check_status():
    """Check status of all TestPilot components"""
    
    print("🔍 TestPilot System Status Check")
    print("=" * 40)
    
    # Check React frontend
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        print("✅ Frontend (React): Running")
    except:
        print("❌ Frontend (React): Not running")
        print("   Start with: cd src/web_interface && npm start")
    
    # Check AI backend
    try:
        response = requests.get("http://localhost:8001", timeout=2)
        data = response.json()
        ai_status = "✅" if data.get("ai_available") else "⚠️"
        print(f"{ai_status} AI Backend: {data.get('status', 'Unknown')}")
        if data.get("ai_available"):
            print("   🤖 Gemini AI: Ready")
        else:
            print("   ❌ Gemini AI: Check API key in .env")
    except:
        print("❌ AI Backend: Not running")
        print("   Start with: python ai_execution_backend.py")
    
    # Check environment file
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            if "AIzaSyDM5YCtLwRUQgTTM8CBiCWtDY9Mr8Dr95M" in content:
                print("✅ API Key: Configured")
            else:
                print("⚠️  API Key: Check .env file")
    else:
        print("❌ .env file: Missing")
    
    # Check key files
    key_files = [
        "ai_execution_backend.py",
        "src/web_interface/src/components/ChatInterface.tsx",
        "src/web_interface/src/components/TestRecorder.tsx",
        "SESSION_SUMMARY.md"
    ]
    
    print("\n📁 Key Files:")
    for file in key_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
    
    print("\n🎯 Quick Test:")
    print("1. Open http://localhost:3000")
    print("2. Go to Tests page → AI Assistant")
    print("3. Type: 'Test a WiFi amplifier'")
    print("4. Should see mermaid diagram + execution results")
    
    print("\n📖 Documentation:")
    print("• SESSION_SUMMARY.md - Full session details")
    print("• CLAUDE.md - Updated with latest status")
    print("• API_SETUP_GUIDE.md - Setup instructions")

if __name__ == "__main__":
    check_status()