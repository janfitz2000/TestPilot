#!/usr/bin/env python3
"""
Real SCPI Instrument Testing Interface
Allows testing actual SCPI instruments via TCP/IP, Serial, or USB
"""

import asyncio
import socket
import serial
import pyvisa
import time
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime

class SCPIInstrumentTester:
    """Test real SCPI instruments with various connection types"""
    
    def __init__(self):
        self.connections = {}
        self.instrument_profiles = {}
        self.test_history = []
        self.logger = logging.getLogger(__name__)
        
    async def discover_instruments(self, connection_type: str = "tcp") -> List[Dict[str, Any]]:
        """Discover SCPI instruments on network or USB"""
        discovered = []
        
        if connection_type == "tcp":
            discovered = await self._discover_tcp_instruments()
        elif connection_type == "usb":
            discovered = await self._discover_usb_instruments()
        elif connection_type == "serial":
            discovered = await self._discover_serial_instruments()
        elif connection_type == "visa":
            discovered = await self._discover_visa_instruments()
            
        return discovered
    
    async def _discover_tcp_instruments(self) -> List[Dict[str, Any]]:
        """Scan network for SCPI instruments"""
        instruments = []
        
        # Common SCPI ports: 5025 (standard), 5024, 80, 8080
        common_ports = [5025, 5024, 80, 8080, 23]
        
        # Scan common instrument IP ranges (you can customize this)
        base_ips = ["192.168.1.", "192.168.0.", "10.0.0.", "172.16.0."]
        
        print("🔍 Scanning network for SCPI instruments...")
        
        for base_ip in base_ips[:1]:  # Limit scan for demo
            for i in range(100, 110):  # Scan .100-.109
                ip = f"{base_ip}{i}"
                for port in common_ports:
                    try:
                        # Quick connection test
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((ip, port))
                        sock.close()
                        
                        if result == 0:
                            # Try to identify instrument
                            identity = await self._identify_instrument_tcp(ip, port)
                            if identity:
                                instruments.append({
                                    "address": f"{ip}:{port}",
                                    "type": "TCP/IP",
                                    "identity": identity,
                                    "connection_method": "tcp"
                                })
                                print(f"   ✅ Found: {identity} at {ip}:{port}")
                    except Exception:
                        continue
                        
        return instruments
    
    async def _discover_visa_instruments(self) -> List[Dict[str, Any]]:
        """Discover instruments using PyVISA"""
        instruments = []
        
        try:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()
            
            for resource in resources:
                try:
                    inst = rm.open_resource(resource)
                    inst.timeout = 2000
                    identity = inst.query("*IDN?").strip()
                    inst.close()
                    
                    instruments.append({
                        "address": resource,
                        "type": "VISA",
                        "identity": identity,
                        "connection_method": "visa"
                    })
                    print(f"   ✅ Found: {identity} at {resource}")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not query {resource}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ VISA discovery failed: {e}")
            
        return instruments
    
    async def _identify_instrument_tcp(self, ip: str, port: int) -> Optional[str]:
        """Try to identify SCPI instrument via TCP"""
        try:
            # Connect and send *IDN? query
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((ip, port))
            
            # Send SCPI identification query
            sock.send(b"*IDN?\n")
            response = sock.recv(1024).decode().strip()
            sock.close()
            
            if response and len(response) > 5:
                return response
                
        except Exception:
            pass
            
        return None
    
    async def connect_to_instrument(self, address: str, connection_method: str = "tcp") -> str:
        """Connect to a specific instrument"""
        connection_id = f"{connection_method}_{address}_{int(time.time())}"
        
        try:
            if connection_method == "tcp":
                ip, port = address.split(":")
                connection = await self._create_tcp_connection(ip, int(port))
            elif connection_method == "visa":
                connection = await self._create_visa_connection(address)
            else:
                raise ValueError(f"Unsupported connection method: {connection_method}")
                
            self.connections[connection_id] = {
                "connection": connection,
                "method": connection_method,
                "address": address,
                "connected_at": datetime.now()
            }
            
            # Get instrument identity
            identity = await self.send_command(connection_id, "*IDN?")
            self.connections[connection_id]["identity"] = identity
            
            print(f"✅ Connected to: {identity}")
            return connection_id
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    async def _create_tcp_connection(self, ip: str, port: int):
        """Create TCP connection to instrument"""
        class TCPConnection:
            def __init__(self, ip, port):
                self.ip = ip
                self.port = port
                self.sock = None
                
            async def connect(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0)
                self.sock.connect((self.ip, self.port))
                
            async def send_command(self, command: str) -> str:
                if not self.sock:
                    await self.connect()
                    
                # Send command
                if not command.endswith('\n'):
                    command += '\n'
                self.sock.send(command.encode())
                
                # Read response if it's a query
                if command.strip().endswith('?'):
                    response = self.sock.recv(1024).decode().strip()
                    return response
                else:
                    return "OK"
                    
            def close(self):
                if self.sock:
                    self.sock.close()
                    
        conn = TCPConnection(ip, port)
        await conn.connect()
        return conn
    
    async def _create_visa_connection(self, address: str):
        """Create VISA connection to instrument"""
        class VISAConnection:
            def __init__(self, address):
                self.address = address
                self.rm = pyvisa.ResourceManager()
                self.inst = None
                
            async def connect(self):
                self.inst = self.rm.open_resource(self.address)
                self.inst.timeout = 5000
                
            async def send_command(self, command: str) -> str:
                if not self.inst:
                    await self.connect()
                    
                if command.strip().endswith('?'):
                    response = self.inst.query(command).strip()
                    return response
                else:
                    self.inst.write(command)
                    return "OK"
                    
            def close(self):
                if self.inst:
                    self.inst.close()
                    
        conn = VISAConnection(address)
        await conn.connect()
        return conn
    
    async def send_command(self, connection_id: str, command: str) -> str:
        """Send SCPI command to connected instrument"""
        if connection_id not in self.connections:
            raise ValueError(f"No connection with ID: {connection_id}")
            
        connection_info = self.connections[connection_id]
        connection = connection_info["connection"]
        
        try:
            print(f"📡 Sending: {command}")
            result = await connection.send_command(command)
            print(f"📨 Response: {result}")
            
            # Log the command
            self.test_history.append({
                "timestamp": datetime.now().isoformat(),
                "connection_id": connection_id,
                "command": command,
                "response": result,
                "instrument": connection_info.get("identity", "Unknown")
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Command failed: {e}"
            print(f"❌ {error_msg}")
            raise
    
    async def run_test_sequence(self, connection_id: str, commands: List[str]) -> Dict[str, Any]:
        """Run a sequence of SCPI commands"""
        results = []
        start_time = time.time()
        
        print(f"\n🚀 Running test sequence ({len(commands)} commands)...")
        
        for i, command in enumerate(commands, 1):
            try:
                print(f"\n[{i}/{len(commands)}] {command}")
                response = await self.send_command(connection_id, command)
                results.append({
                    "command": command,
                    "response": response,
                    "success": True
                })
                
                # Add small delay between commands
                await asyncio.sleep(0.1)
                
            except Exception as e:
                results.append({
                    "command": command,
                    "response": str(e),
                    "success": False
                })
                print(f"❌ Command failed: {e}")
        
        execution_time = time.time() - start_time
        
        summary = {
            "total_commands": len(commands),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "execution_time": execution_time,
            "results": results
        }
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Successful: {summary['successful']}/{summary['total_commands']}")
        print(f"   ❌ Failed: {summary['failed']}/{summary['total_commands']}")
        print(f"   ⏱️  Time: {execution_time:.2f} seconds")
        
        return summary
    
    def disconnect(self, connection_id: str):
        """Disconnect from instrument"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]["connection"]
            connection.close()
            del self.connections[connection_id]
            print(f"✅ Disconnected from {connection_id}")
    
    def get_test_history(self) -> List[Dict[str, Any]]:
        """Get test command history"""
        return self.test_history
    
    def export_test_results(self, filename: str = None):
        """Export test results to JSON file"""
        if not filename:
            filename = f"scpi_test_results_{int(time.time())}.json"
            
        data = {
            "test_session": {
                "timestamp": datetime.now().isoformat(),
                "total_commands": len(self.test_history)
            },
            "connections": {
                conn_id: {
                    "address": info["address"],
                    "method": info["method"],
                    "identity": info.get("identity", "Unknown")
                }
                for conn_id, info in self.connections.items()
            },
            "command_history": self.test_history
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"📄 Test results exported to: {filename}")

# Demo function for testing
async def demo_scpi_testing():
    """Demonstrate SCPI instrument testing"""
    
    print("🧪 SCPI Instrument Testing Demo")
    print("=" * 40)
    
    tester = SCPIInstrumentTester()
    
    # 1. Discover instruments
    print("\n1️⃣ Discovering instruments...")
    tcp_instruments = await tester.discover_instruments("tcp")
    visa_instruments = await tester.discover_instruments("visa")
    
    all_instruments = tcp_instruments + visa_instruments
    
    if not all_instruments:
        print("⚠️  No instruments found. Testing with simulated instrument...")
        # For demo purposes, you can test with a specific IP if you have one
        # Replace with your instrument's actual IP address
        print("\n💡 To test with real instrument, update the IP address in the code")
        return
    
    # 2. Connect to first found instrument
    print(f"\n2️⃣ Connecting to instrument...")
    instrument = all_instruments[0]
    connection_id = await tester.connect_to_instrument(
        instrument["address"], 
        instrument["connection_method"]
    )
    
    # 3. Run basic identification sequence
    print(f"\n3️⃣ Running basic SCPI tests...")
    basic_commands = [
        "*IDN?",           # Instrument identification
        "*OPC?",           # Operation complete query
        ":SYST:ERR?",      # System error query
        "*TST?",           # Self-test query (if supported)
        ":SYST:VERS?"      # SCPI version query
    ]
    
    results = await tester.run_test_sequence(connection_id, basic_commands)
    
    # 4. Export results
    tester.export_test_results()
    
    # 5. Disconnect
    tester.disconnect(connection_id)
    
    print(f"\n✅ Demo complete!")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the demo
    asyncio.run(demo_scpi_testing())