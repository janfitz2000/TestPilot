#!/usr/bin/env python3
"""
Quick Test of New Execution-Based AI System
"""

import requests
import json

def test_new_ai_system():
    """Test the execution-based AI system"""
    
    print("🧪 Testing NEW TestPilot AI System")
    print("=" * 50)
    
    # Test requests that should trigger execution
    test_requests = [
        "Test a 2.4GHz WiFi amplifier for gain",
        "Check power supply regulation",
        "Measure signal on oscilloscope",
        "Analyze RF characteristics"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}️⃣ Testing: '{request}'")
        
        try:
            response = requests.post(
                "http://localhost:8001/chat",
                json={"message": request},
                timeout=15
            )
            
            if response.ok:
                data = response.json()
                print(f"✅ Response Type: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'test_execution':
                    print("🧪 TEST WAS EXECUTED!")
                    metadata = data.get('metadata', {})
                    print(f"   Execution Time: {metadata.get('execution_time', 'N/A')}")
                    print(f"   Measurements: {metadata.get('measurements', 'None')}")
                    print(f"   Mermaid Diagram: {'✅ Generated' if metadata.get('mermaid_diagram') else '❌ Missing'}")
                else:
                    print("📝 Regular AI response (no execution)")
                    
                print(f"Preview: {data['response'][:100]}...")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Summary:")
    print("If you see 'TEST WAS EXECUTED!' above, your new system is working!")
    print("The web interface at http://localhost:3000 should now:")
    print("✅ Execute actual tests instead of just describing them")
    print("✅ Show mermaid diagrams automatically")
    print("✅ Display real measurement data")
    print("✅ Provide scientific analysis")

if __name__ == "__main__":
    test_new_ai_system()