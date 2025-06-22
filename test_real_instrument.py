#!/usr/bin/env python3
"""
Quick Test Script for Real SCPI Instruments
Configure this script with your actual instrument IP and test basic SCPI communication
"""

import asyncio
import sys
import socket
from src.ai_orchestrator.scpi_tester import SCPIInstrumentTester

async def test_specific_instrument():
    """Test a specific SCPI instrument - UPDATE THE IP BELOW"""
    
    # 🔧 CONFIGURE YOUR INSTRUMENT HERE:
    INSTRUMENT_IP = "192.168.1.100"  # ← Change this to your instrument's IP
    INSTRUMENT_PORT = 5025           # ← Most SCPI instruments use port 5025
    
    print("🧪 TestPilot: Real SCPI Instrument Test")
    print("=" * 50)
    print(f"Target Instrument: {INSTRUMENT_IP}:{INSTRUMENT_PORT}")
    print()
    
    # Quick connectivity test
    print("1️⃣ Testing connectivity...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        result = sock.connect_ex((INSTRUMENT_IP, INSTRUMENT_PORT))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Network connection successful to {INSTRUMENT_IP}:{INSTRUMENT_PORT}")
        else:
            print(f"   ❌ Cannot connect to {INSTRUMENT_IP}:{INSTRUMENT_PORT}")
            print("   💡 Check:")
            print("      • Instrument IP address is correct")
            print("      • Instrument is powered on")
            print("      • Network cable is connected")
            print("      • SCPI interface is enabled")
            return
            
    except Exception as e:
        print(f"   ❌ Network test failed: {e}")
        return
    
    # Initialize SCPI tester
    tester = SCPIInstrumentTester()
    
    try:
        print("\n2️⃣ Connecting to instrument...")
        connection_id = await tester.connect_to_instrument(
            f"{INSTRUMENT_IP}:{INSTRUMENT_PORT}", 
            "tcp"
        )
        
        print("\n3️⃣ Running basic SCPI commands...")
        
        # Essential SCPI commands that most instruments support
        basic_commands = [
            "*IDN?",              # Instrument identification
            "*OPC?",              # Operation complete query
            ":SYST:ERR?",         # System error query  
            ":SYST:VERS?",        # SCPI version
        ]
        
        results = await tester.run_test_sequence(connection_id, basic_commands)
        
        print("\n4️⃣ Testing instrument-specific commands...")
        
        # Try some common measurement commands (will fail if not supported)
        advanced_commands = [
            ":FREQ:CENT?",        # Center frequency (for VNAs/Spec Analyzers)
            ":POW?",              # Power level (for Signal Generators)
            ":MEAS:S11?",         # S11 measurement (for VNAs)
            ":CALC:DATA:FDAT?",   # Formatted data (for VNAs)
        ]
        
        print("   Testing advanced commands (some may fail if not supported):")
        for cmd in advanced_commands:
            try:
                response = await tester.send_command(connection_id, cmd)
                print(f"   ✅ {cmd}: {response}")
            except Exception as e:
                print(f"   ⚠️  {cmd}: Not supported or failed ({str(e)[:50]})")
        
        # Export test results
        print("\n5️⃣ Saving test results...")
        tester.export_test_results(f"instrument_test_{INSTRUMENT_IP.replace('.', '_')}.json")
        
        # Disconnect
        tester.disconnect(connection_id)
        
        print(f"\n🎯 Test Summary:")
        print(f"   • Successfully connected to {INSTRUMENT_IP}")
        print(f"   • Basic SCPI commands: {results['successful']}/{results['total_commands']} successful")
        print(f"   • Test completed in {results['execution_time']:.1f} seconds")
        print(f"   • Results saved to instrument_test_{INSTRUMENT_IP.replace('.', '_')}.json")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Verify instrument IP address")
        print("   • Check if SCPI over TCP/IP is enabled")
        print("   • Try port 23 (Telnet) instead of 5025")
        print("   • Some instruments require login credentials")

async def discover_network_instruments():
    """Scan network for SCPI instruments"""
    print("🔍 Network Instrument Discovery")
    print("=" * 40)
    
    tester = SCPIInstrumentTester()
    
    print("Scanning for TCP/IP instruments...")
    tcp_instruments = await tester.discover_instruments("tcp")
    
    if tcp_instruments:
        print(f"\n✅ Found {len(tcp_instruments)} instruments:")
        for instrument in tcp_instruments:
            print(f"   • {instrument['identity']} at {instrument['address']}")
            
        # Test first found instrument
        print("\n🧪 Testing first found instrument...")
        first_instrument = tcp_instruments[0]
        connection_id = await tester.connect_to_instrument(
            first_instrument["address"],
            first_instrument["connection_method"]
        )
        
        # Quick test
        await tester.send_command(connection_id, "*IDN?")
        await tester.send_command(connection_id, "*OPC?")
        
        tester.disconnect(connection_id)
        
    else:
        print("❌ No instruments found on network")
        print("\n💡 Make sure instruments are:")
        print("   • Connected to same network")
        print("   • Have SCPI/TCP enabled")
        print("   • Using standard ports (5025, 23, 80)")

def main():
    """Main function - choose your test mode"""
    print("TestPilot SCPI Instrument Tester")
    print("Choose test mode:")
    print("1. Test specific instrument (configure IP in script)")
    print("2. Auto-discover instruments on network")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = input("\nEnter choice (1 or 2): ").strip()
    
    if mode == "1":
        asyncio.run(test_specific_instrument())
    elif mode == "2":
        asyncio.run(discover_network_instruments())
    else:
        print("❌ Invalid choice. Use 1 or 2.")

if __name__ == "__main__":
    main()