#!/usr/bin/env python3
"""
TestPilot + Gemini Demo
Shows how Gemini AI will power your test automation platform
"""

import google.generativeai as genai
import json
import time

def demo_ai_test_automation():
    """Demonstrate AI-powered test automation with Gemini"""
    
    # Your API key
    API_KEY = "AIzaSyDM5YCtLwRUQgTTM8CBiCWtDY9Mr8Dr95M"
    
    print("🚀 TestPilot + Gemini AI Demo")
    print("=" * 50)
    print("This shows how AI will power your test automation!")
    print()
    
    try:
        # Configure Gemini
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Scenario 1: Natural Language Test Planning
        print("1️⃣ Natural Language Test Planning")
        print("=" * 40)
        
        user_request = "I need to test a 2.4GHz WiFi power amplifier for gain, harmonics, and ACPR compliance. The amplifier should have 20±2dB gain."
        
        print(f"User says: \"{user_request}\"")
        print("\n🤖 AI generating test plan...")
        
        test_plan_prompt = f"""
        You are an expert RF test engineer. Generate a detailed test plan for this request:
        "{user_request}"
        
        Return your response as JSON with this structure:
        {{
            "test_objectives": ["list of objectives"],
            "required_instruments": ["list of instruments"],
            "test_procedures": [
                {{"step": 1, "action": "description", "scpi_commands": ["list of commands"], "expected_result": "description"}},
                {{"step": 2, "action": "description", "scpi_commands": ["list of commands"], "expected_result": "description"}}
            ],
            "pass_criteria": ["list of criteria"],
            "estimated_duration": "time estimate"
        }}
        """
        
        response = model.generate_content(test_plan_prompt)
        print("\n✅ AI Test Plan Generated:")
        print(response.text[:400] + "...")
        
        # Scenario 2: SCPI Command Generation
        print("\n\n2️⃣ SCPI Command Generation")
        print("=" * 40)
        
        scpi_prompt = """
        Generate specific SCPI commands for testing a WiFi amplifier:
        1. Set signal generator to 2.45GHz, -5dBm
        2. Configure spectrum analyzer for harmonic measurement
        3. Measure fundamental and 2nd harmonic
        
        Return actual SCPI commands that would work with Keysight instruments.
        """
        
        print("🤖 AI generating SCPI commands...")
        scpi_response = model.generate_content(scpi_prompt)
        print("\n✅ AI Generated SCPI Commands:")
        print(scpi_response.text[:300] + "...")
        
        # Scenario 3: Data Analysis
        print("\n\n3️⃣ Intelligent Data Analysis")
        print("=" * 40)
        
        # Simulate test results
        test_data = {
            "measurements": [
                {"frequency": 2.45e9, "gain": 20.1, "harmonics": -42.3},
                {"frequency": 2.46e9, "gain": 19.8, "harmonics": -41.8},
                {"frequency": 2.47e9, "gain": 20.3, "harmonics": -43.1}
            ],
            "specifications": {"gain_min": 18, "gain_max": 22, "harmonics_max": -40}
        }
        
        analysis_prompt = f"""
        Analyze these WiFi amplifier test results and provide insights:
        
        Test Data: {json.dumps(test_data, indent=2)}
        
        Determine:
        1. Pass/fail status for each measurement
        2. Overall compliance assessment  
        3. Any trends or issues to note
        4. Recommendations for next steps
        
        Be specific about which measurements pass/fail and why.
        """
        
        print("🤖 AI analyzing test results...")
        analysis_response = model.generate_content(analysis_prompt)
        print("\n✅ AI Analysis:")
        print(analysis_response.text[:400] + "...")
        
        # Scenario 4: Driver Generation from Manual
        print("\n\n4️⃣ AI Driver Generation")
        print("=" * 40)
        
        manual_excerpt = """
        Keysight E5071C Network Analyzer Commands:
        
        *IDN? - Returns instrument identification
        :SENS:FREQ:STAR <frequency> - Sets start frequency in Hz
        :SENS:FREQ:STOP <frequency> - Sets stop frequency in Hz  
        :CALC:DATA:FDAT? - Gets formatted measurement data
        :TRIG:SING - Triggers single sweep
        """
        
        driver_prompt = f"""
        Generate a Python driver class from this instrument manual excerpt:
        
        {manual_excerpt}
        
        Create a complete Python class with:
        1. Connection management
        2. Methods for each SCPI command
        3. Error handling
        4. Documentation
        
        Use PyVISA for communication.
        """
        
        print("🤖 AI generating Python driver...")
        driver_response = model.generate_content(driver_prompt)
        print("\n✅ AI Generated Driver Code:")
        print(driver_response.text[:300] + "...")
        
        print("\n\n🎯 TestPilot AI Integration Complete!")
        print("=" * 50)
        print("Your TestPilot system can now:")
        print("✅ Generate test plans from natural language")
        print("✅ Create SCPI command sequences automatically") 
        print("✅ Analyze measurement data intelligently")
        print("✅ Generate instrument drivers from manuals")
        print("✅ Provide real-time test insights and recommendations")
        print()
        print("🌐 Ready to use at: http://localhost:3000")
        print("💬 Try: 'Test a WiFi amplifier at 2.4GHz'")
        
    except Exception as e:
        if "429" in str(e):
            print("⏳ Rate limit reached. Wait a few minutes and try again.")
            print("💡 Your API key is working - just hit the rate limit!")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_ai_test_automation()