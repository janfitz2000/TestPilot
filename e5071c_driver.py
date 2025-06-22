"""
Auto-generated driver for E5071C
Generated on: 2025-06-15 00:20:12
Manufacturer: Keysight
"""

import pyvisa
import time
from typing import Optional, Union, List
import logging

class E5071CDriver:
    """
    Python driver for E5071C Keysight
    
    Specifications:
    - Frequency Range: 300 kHz to 20 GHz
    - Power Range: See manual
    """
    
    def __init__(self, address: str, timeout: int = 5000):
        """
        Initialize instrument connection
        
        Args:
            address: VISA address (e.g., 'TCPIP::192.168.1.100::INSTR')
            timeout: Command timeout in milliseconds
        """
        self.address = address
        self.timeout = timeout
        self.instrument = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to instrument"""
        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.address)
            self.instrument.timeout = self.timeout
            
            # Verify connection
            identity = self.instrument.query("*IDN?")
            self.logger.info(f"Connected to: {identity}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from instrument"""
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            
    def write(self, command: str):
        """Send command to instrument"""
        if not self.instrument:
            raise RuntimeError("Not connected to instrument")
        self.instrument.write(command)
        
    def query(self, command: str) -> str:
        """Send query command and return response"""
        if not self.instrument:
            raise RuntimeError("Not connected to instrument")
        return self.instrument.query(command).strip()
        
    def query_float(self, command: str) -> float:
        """Send query command and return float response"""
        response = self.query(command)
        return float(response)
        
    def reset(self):
        """Reset instrument to default state"""
        self.write("*RST")
        self.write("*CLS")  # Clear status
        
    def get_identity(self) -> str:
        """Get instrument identification"""
        return self.query("*IDN?")
        
    def self_test(self) -> bool:
        """Run instrument self-test"""
        try:
            result = self.query("*TST?")
            return result == "0"  # 0 = pass
        except:
            return False
            
    def get_error(self) -> str:
        """Get last error message"""
        return self.query(":SYST:ERR?")
        
    def wait_for_operation_complete(self, timeout: float = 10.0):
        """Wait for operation to complete"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.query("*OPC?") == "1":
                return
            time.sleep(0.1)
        raise TimeoutError("Operation did not complete within timeout")


    # Utility Methods
    
    def configure_for_measurement(self):
        """Configure instrument for typical measurements"""
        self.reset()
        self.wait_for_operation_complete()
        
    def get_measurement_data(self) -> dict:
        """Get comprehensive measurement data"""
        data = {
            "timestamp": time.time(),
            "identity": self.get_identity(),
            "errors": self.get_error()
        }
        return data
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

# Example usage:
# with {self.instrument_info.get("model", "Instrument").replace("-", "_")}Driver("TCPIP::192.168.1.100::INSTR") as inst:
#     print(inst.get_identity())
#     inst.configure_for_measurement()
