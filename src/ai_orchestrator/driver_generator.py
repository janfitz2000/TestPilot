#!/usr/bin/env python3
"""
AI Driver Generator from Instrument Manuals
Analyzes instrument manuals and generates custom Python drivers
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

@dataclass
class SCPICommand:
    """Represents a SCPI command extracted from manual"""
    command: str
    description: str
    parameters: List[str]
    response_type: str
    example: str
    category: str

@dataclass
class InstrumentCapability:
    """Represents instrument measurement capability"""
    name: str
    frequency_range: Optional[str]
    power_range: Optional[str]
    accuracy: Optional[str]
    commands: List[SCPICommand]

class AIDriverGenerator:
    """Generate Python drivers from instrument manuals using AI"""
    
    def __init__(self):
        self.manual_content = ""
        self.extracted_commands = []
        self.instrument_info = {}
        self.generated_driver = ""
        
    def analyze_manual(self, manual_text: str) -> Dict[str, Any]:
        """Analyze instrument manual and extract key information"""
        self.manual_content = manual_text
        
        print("🧠 Analyzing instrument manual...")
        
        # Extract basic instrument information
        self.instrument_info = self._extract_instrument_info(manual_text)
        
        # Extract SCPI commands
        self.extracted_commands = self._extract_scpi_commands(manual_text)
        
        # Categorize capabilities
        capabilities = self._categorize_capabilities()
        
        analysis = {
            "instrument_info": self.instrument_info,
            "command_count": len(self.extracted_commands),
            "capabilities": capabilities,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Analysis complete:")
        print(f"   📊 Found {len(self.extracted_commands)} SCPI commands")
        print(f"   🎯 Identified {len(capabilities)} capabilities")
        
        return analysis
    
    def _extract_instrument_info(self, manual_text: str) -> Dict[str, Any]:
        """Extract basic instrument information"""
        
        # Common patterns for instrument info
        patterns = {
            "model": [
                r"Model:?\s*([A-Z0-9\-]+)",
                r"(\w+\s*\d+[A-Z]*)\s+User",
                r"(\w+\s*E\d+[A-Z]*)",  # Keysight pattern
                r"(\w+\s*R&S\s*\w+)"   # R&S pattern
            ],
            "manufacturer": [
                r"(Keysight|Agilent|Hewlett.Packard|HP)",
                r"(Rohde.{0,3}Schwarz|R&S)",
                r"(Tektronix|Tek)",
                r"(Anritsu)",
                r"(Rigol)"
            ],
            "frequency_range": [
                r"Frequency Range:?\s*([0-9.]+ ?[kMG]?Hz\s*(?:to|-)\s*[0-9.]+ ?[kMG]?Hz)",
                r"([0-9.]+ ?[kMG]?Hz\s*(?:to|-)\s*[0-9.]+ ?[kMG]?Hz)",
            ],
            "power_range": [
                r"Power Range:?\s*([-+]?[0-9.]+ ?dBm\s*(?:to|-)\s*[-+]?[0-9.]+ ?dBm)",
                r"Output Power:?\s*([-+]?[0-9.]+ ?dBm\s*(?:to|-)\s*[-+]?[0-9.]+ ?dBm)",
            ]
        }
        
        info = {}
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, manual_text, re.IGNORECASE)
                if match:
                    info[key] = match.group(1).strip()
                    break
                    
        return info
    
    def _extract_scpi_commands(self, manual_text: str) -> List[SCPICommand]:
        """Extract SCPI commands from manual text"""
        commands = []
        
        # Pattern to match SCPI commands
        scpi_patterns = [
            # Standard SCPI command pattern
            r"(?:^|\n)\s*([:\*][A-Z][A-Z0-9:\?]*(?:\[[A-Z0-9,]*\])?)\s*(.{0,200}?)(?=\n[:\*]|\n\n|\n[A-Z]|\Z)",
            # Alternative pattern
            r"(?:Command|SCPI):\s*([:\*][A-Z][A-Z0-9:\?]*)\s*\n?(.*?)(?=\n\n|\nCommand|\nSCPI|\Z)"
        ]
        
        for pattern in scpi_patterns:
            matches = re.finditer(pattern, manual_text, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                command = match.group(1).strip()
                description = match.group(2).strip()
                
                # Skip if too short or doesn't look like SCPI
                if len(command) < 3 or not (command.startswith(':') or command.startswith('*')):
                    continue
                
                # Extract parameters and response type
                parameters = self._extract_parameters(description)
                response_type = "string" if command.endswith('?') else "none"
                
                # Categorize command
                category = self._categorize_command(command)
                
                scpi_cmd = SCPICommand(
                    command=command,
                    description=description[:200],  # Limit description length
                    parameters=parameters,
                    response_type=response_type,
                    example=self._generate_example(command, parameters),
                    category=category
                )
                
                commands.append(scpi_cmd)
        
        # Remove duplicates
        unique_commands = []
        seen = set()
        for cmd in commands:
            if cmd.command not in seen:
                unique_commands.append(cmd)
                seen.add(cmd.command)
                
        return unique_commands
    
    def _extract_parameters(self, description: str) -> List[str]:
        """Extract parameter information from command description"""
        parameters = []
        
        # Look for parameter patterns
        param_patterns = [
            r"<([^>]+)>",  # <parameter>
            r"\{([^}]+)\}",  # {parameter}
            r"Parameter:?\s*([A-Za-z0-9_]+)",
            r"Range:?\s*([0-9.]+ ?(?:to|-) ?[0-9.]+)",
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            parameters.extend(matches)
            
        return parameters[:5]  # Limit to 5 parameters
    
    def _categorize_command(self, command: str) -> str:
        """Categorize SCPI command by function"""
        command_lower = command.lower()
        
        categories = {
            "measurement": ["meas", "calc", "fetc", "read"],
            "configuration": ["conf", "sens", "sour", "outp", "inp"],
            "system": ["syst", "disp", "mem", "stor"],
            "calibration": ["cal", "corr"],
            "trigger": ["trig", "init", "abor"],
            "status": ["stat", "oper", "ques"],
            "common": ["*"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in command_lower for keyword in keywords):
                return category
                
        return "other"
    
    def _generate_example(self, command: str, parameters: List[str]) -> str:
        """Generate usage example for command"""
        if command.endswith('?'):
            return f'result = instrument.query("{command}")'
        else:
            if parameters:
                param_example = ", ".join([f'"{p}"' for p in parameters[:2]])
                return f'instrument.write("{command}", {param_example})'
            else:
                return f'instrument.write("{command}")'
    
    def _categorize_capabilities(self) -> List[InstrumentCapability]:
        """Group commands into functional capabilities"""
        capabilities = {}
        
        for cmd in self.extracted_commands:
            category = cmd.category
            
            if category not in capabilities:
                capabilities[category] = InstrumentCapability(
                    name=category.title(),
                    frequency_range=self.instrument_info.get("frequency_range"),
                    power_range=self.instrument_info.get("power_range"),
                    accuracy=None,
                    commands=[]
                )
                
            capabilities[category].commands.append(cmd)
            
        return list(capabilities.values())
    
    def generate_driver(self, instrument_name: str, analysis: Dict[str, Any]) -> str:
        """Generate Python driver code from analysis"""
        
        print(f"🔧 Generating Python driver for {instrument_name}...")
        
        # Generate driver class
        driver_code = self._generate_driver_template(instrument_name, analysis)
        
        # Add methods for each capability
        for capability in analysis["capabilities"]:
            driver_code += self._generate_capability_methods(capability)
        
        # Add utility methods
        driver_code += self._generate_utility_methods()
        
        self.generated_driver = driver_code
        
        print(f"✅ Driver generated ({len(driver_code)} characters)")
        
        return driver_code
    
    def _generate_driver_template(self, instrument_name: str, analysis: Dict[str, Any]) -> str:
        """Generate driver class template"""
        
        info = analysis["instrument_info"]
        model = info.get("model", instrument_name)
        manufacturer = info.get("manufacturer", "Unknown")
        
        template = f'''"""
Auto-generated driver for {model}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Manufacturer: {manufacturer}
"""

import pyvisa
import time
from typing import Optional, Union, List
import logging

class {model.replace("-", "_").replace(" ", "_")}Driver:
    """
    Python driver for {model} {manufacturer}
    
    Specifications:
    - Frequency Range: {info.get("frequency_range", "See manual")}
    - Power Range: {info.get("power_range", "See manual")}
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
            self.logger.info(f"Connected to: {{identity}}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {{e}}")
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

'''
        
        return template
    
    def _generate_capability_methods(self, capability: InstrumentCapability) -> str:
        """Generate methods for instrument capability"""
        
        methods = f"\n    # {capability.name} Methods\n"
        
        for cmd in capability.commands[:10]:  # Limit to 10 commands per capability
            method_name = self._command_to_method_name(cmd.command)
            
            if cmd.command.endswith('?'):
                # Query method
                methods += f'''
    def {method_name}(self) -> str:
        """
        {cmd.description[:100]}
        
        Returns:
            str: {cmd.command} response
        """
        return self.query("{cmd.command}")
'''
            else:
                # Write method
                param_str = ""
                if cmd.parameters:
                    params = cmd.parameters[:3]  # Limit parameters
                    param_str = ", " + ", ".join([f"{p}: Union[str, float]" for p in params])
                    param_usage = ", ".join([f"{{{p}}}" for p in params])
                    command_with_params = f"{cmd.command} {param_usage}"
                else:
                    command_with_params = cmd.command
                    
                methods += f'''
    def {method_name}(self{param_str}):
        """
        {cmd.description[:100]}
        """
        self.write("{command_with_params}")
'''
        
        return methods
    
    def _command_to_method_name(self, command: str) -> str:
        """Convert SCPI command to Python method name"""
        # Remove SCPI syntax and convert to snake_case
        name = command.replace("*", "").replace(":", "_").replace("?", "_query")
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        name = re.sub(r"_+", "_", name).strip("_").lower()
        
        # Ensure it starts with letter
        if name and name[0].isdigit():
            name = "cmd_" + name
            
        return name or "unknown_command"
    
    def _generate_utility_methods(self) -> str:
        """Generate utility methods for the driver"""
        
        return '''
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
'''
    
    def save_driver(self, filename: str = None) -> str:
        """Save generated driver to file"""
        if not filename:
            model = self.instrument_info.get("model", "instrument")
            filename = f"{model.lower().replace('-', '_').replace(' ', '_')}_driver.py"
            
        with open(filename, 'w') as f:
            f.write(self.generated_driver)
            
        print(f"💾 Driver saved to: {filename}")
        return filename

# Demo function
async def demo_driver_generation():
    """Demonstrate driver generation from manual excerpt"""
    
    # Sample manual excerpt (you would paste your real manual here)
    sample_manual = """
    Model: E5071C Network Analyzer
    Manufacturer: Keysight Technologies
    Frequency Range: 300 kHz to 20 GHz
    
    SCPI Commands:
    
    *IDN?
    Returns instrument identification string
    
    :SENS:FREQ:STAR <frequency>
    Sets start frequency
    Parameter: frequency in Hz
    Range: 300e3 to 20e9
    
    :SENS:FREQ:STOP <frequency>  
    Sets stop frequency
    Parameter: frequency in Hz
    
    :SENS:FREQ:STAR?
    Queries start frequency
    Returns: frequency in Hz
    
    :CALC:DATA:FDAT?
    Gets formatted measurement data
    Returns: comma-separated values
    
    :SENS:SWE:POIN <points>
    Sets number of sweep points
    Parameter: points (1 to 32001)
    
    :TRIG:SING
    Triggers single sweep
    
    :CALC:PAR:SEL 'S11'
    Selects S11 parameter for measurement
    """
    
    print("🚀 AI Driver Generator Demo")
    print("=" * 40)
    
    generator = AIDriverGenerator()
    
    # 1. Analyze manual
    analysis = generator.analyze_manual(sample_manual)
    
    # 2. Generate driver
    driver_code = generator.generate_driver("E5071C", analysis)
    
    # 3. Save driver
    filename = generator.save_driver()
    
    print(f"\n✅ Demo complete! Generated driver: {filename}")
    print(f"\nGenerated {len(generator.extracted_commands)} methods from manual")

if __name__ == "__main__":
    asyncio.run(demo_driver_generation())