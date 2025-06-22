#!/usr/bin/env python3
"""
TestPilot MCP Server - Exposes test automation capabilities to AI models
Model Context Protocol (MCP) server for instrument control and test management
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx
import logging

# MCP Protocol Implementation
class MCPServer:
    """MCP Server for TestPilot test automation capabilities"""
    
    def __init__(self):
        self.tools = self._define_tools()
        self.base_url = "http://localhost"
        self.logger = logging.getLogger(__name__)
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for AI models"""
        return [
            {
                "name": "list_instruments",
                "description": "List all available test instruments",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "connect_instrument", 
                "description": "Connect to a specific test instrument",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "instrument_id": {
                            "type": "string",
                            "description": "ID of the instrument to connect"
                        }
                    },
                    "required": ["instrument_id"]
                }
            },
            {
                "name": "send_scpi_command",
                "description": "Send SCPI command to an instrument",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "instrument_id": {
                            "type": "string",
                            "description": "ID of the target instrument"
                        },
                        "command": {
                            "type": "string",
                            "description": "SCPI command to send (e.g., '*IDN?', ':MEAS:VOLT?')"
                        }
                    },
                    "required": ["instrument_id", "command"]
                }
            },
            {
                "name": "create_workflow",
                "description": "Create a new test workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the workflow"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Description of what the workflow does"
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string"},
                                    "instrument_id": {"type": "string"},
                                    "command": {"type": "string"},
                                    "expected_result": {"type": "string"}
                                }
                            },
                            "description": "Array of workflow steps"
                        }
                    },
                    "required": ["name", "description", "steps"]
                }
            },
            {
                "name": "execute_workflow",
                "description": "Execute a test workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow to execute"
                        }
                    },
                    "required": ["workflow_id"]
                }
            },
            {
                "name": "analyze_measurement_data",
                "description": "Analyze measurement data and provide insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Array of measurement values"
                        },
                        "measurement_type": {
                            "type": "string",
                            "description": "Type of measurement (voltage, current, frequency, etc.)"
                        }
                    },
                    "required": ["data", "measurement_type"]
                }
            }
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls from AI models"""
        try:
            if tool_name == "list_instruments":
                return await self._list_instruments()
            elif tool_name == "connect_instrument":
                return await self._connect_instrument(arguments["instrument_id"])
            elif tool_name == "send_scpi_command":
                return await self._send_scpi_command(
                    arguments["instrument_id"], 
                    arguments["command"]
                )
            elif tool_name == "create_workflow":
                return await self._create_workflow(arguments)
            elif tool_name == "execute_workflow":
                return await self._execute_workflow(arguments["workflow_id"])
            elif tool_name == "analyze_measurement_data":
                return await self._analyze_data(
                    arguments["data"], 
                    arguments["measurement_type"]
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
    
    async def _list_instruments(self) -> Dict[str, Any]:
        """Get list of available instruments"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}:8002/instruments")
                if response.status_code == 200:
                    instruments = response.json()
                    return {
                        "success": True,
                        "instruments": instruments,
                        "count": len(instruments)
                    }
                else:
                    return {"error": f"Failed to list instruments: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    async def _connect_instrument(self, instrument_id: str) -> Dict[str, Any]:
        """Connect to a specific instrument"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}:8002/instruments/{instrument_id}/connect")
                if response.status_code == 200:
                    return {"success": True, "message": f"Connected to instrument {instrument_id}"}
                else:
                    return {"error": f"Failed to connect: {response.status_code}"}
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}
    
    async def _send_scpi_command(self, instrument_id: str, command: str) -> Dict[str, Any]:
        """Send SCPI command to instrument"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {"command": command}
                response = await client.post(
                    f"{self.base_url}:8002/instruments/{instrument_id}/command",
                    json=payload
                )
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "command": command,
                        "response": result.get("response"),
                        "instrument_id": instrument_id
                    }
                else:
                    return {"error": f"Command failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}
    
    async def _create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new test workflow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}:8003/api/v1/workflows",
                    json=workflow_data
                )
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "workflow_id": result.get("id"),
                        "message": f"Created workflow: {workflow_data['name']}"
                    }
                else:
                    return {"error": f"Workflow creation failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Workflow creation failed: {str(e)}"}
    
    async def _execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a test workflow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}:8003/api/v1/workflows/{workflow_id}/execute"
                )
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "execution_id": result.get("execution_id"),
                        "status": result.get("status", "started")
                    }
                else:
                    return {"error": f"Workflow execution failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Workflow execution failed: {str(e)}"}
    
    async def _analyze_data(self, data: List[float], measurement_type: str) -> Dict[str, Any]:
        """Analyze measurement data"""
        try:
            # Simple statistical analysis
            if not data:
                return {"error": "No data provided"}
            
            avg = sum(data) / len(data)
            min_val = min(data)
            max_val = max(data)
            
            # Calculate standard deviation
            variance = sum((x - avg) ** 2 for x in data) / len(data)
            std_dev = variance ** 0.5
            
            # Basic analysis based on measurement type
            analysis = {
                "statistics": {
                    "average": avg,
                    "minimum": min_val,
                    "maximum": max_val,
                    "std_deviation": std_dev,
                    "sample_count": len(data)
                },
                "measurement_type": measurement_type,
                "insights": []
            }
            
            # Add measurement-specific insights
            if measurement_type.lower() == "voltage":
                if std_dev > avg * 0.1:
                    analysis["insights"].append("High voltage variation detected - check for noise or instability")
                if min_val < 0:
                    analysis["insights"].append("Negative voltages detected - verify measurement setup")
            elif measurement_type.lower() == "frequency":
                stability_ratio = std_dev / avg * 100
                analysis["insights"].append(f"Frequency stability: ±{stability_ratio:.3f}%")
                if stability_ratio > 1:
                    analysis["insights"].append("Poor frequency stability - check oscillator or PLL")
            
            return {"success": True, "analysis": analysis}
            
        except Exception as e:
            return {"error": f"Data analysis failed: {str(e)}"}

# Example usage demonstrating AI-driven test flow
async def demonstrate_ai_workflow():
    """Demonstrate how an AI model would use the MCP server"""
    
    print("🤖 AI-Driven Test Automation Demonstration")
    print("=" * 50)
    
    mcp = MCPServer()
    
    # 1. AI discovers available instruments
    print("\n1. Discovering available instruments...")
    instruments_result = await mcp.handle_tool_call("list_instruments", {})
    print(f"Result: {json.dumps(instruments_result, indent=2)}")
    
    # 2. AI would analyze requirements and select instruments
    print("\n2. AI analyzing test requirements:")
    print("   Task: Test RF amplifier gain at 1GHz")
    print("   Selected instruments: Signal Generator, Spectrum Analyzer")
    
    # 3. AI creates test workflow
    print("\n3. Creating automated test workflow...")
    workflow_data = {
        "name": "RF Amplifier Gain Test",
        "description": "Measure amplifier gain at 1GHz with swept power levels",
        "steps": [
            {
                "action": "configure_signal_generator",
                "instrument_id": "sig_gen_1",
                "command": ":FREQ 1e9; :POW -30",
                "expected_result": "Signal generator configured for 1GHz, -30dBm"
            },
            {
                "action": "measure_output_power", 
                "instrument_id": "spectrum_analyzer_1",
                "command": ":CALC:MARK1:MAX",
                "expected_result": "Peak power measurement"
            },
            {
                "action": "calculate_gain",
                "instrument_id": "virtual",
                "command": "gain = output_power - input_power",
                "expected_result": "Gain calculation in dB"
            }
        ]
    }
    
    workflow_result = await mcp.handle_tool_call("create_workflow", workflow_data)
    print(f"Result: {json.dumps(workflow_result, indent=2)}")
    
    # 4. AI analyzes measurement data
    print("\n4. Analyzing measurement data...")
    sample_gain_data = [15.2, 15.3, 15.1, 15.4, 15.0, 15.2, 15.3]  # Sample gain measurements in dB
    analysis_result = await mcp.handle_tool_call("analyze_measurement_data", {
        "data": sample_gain_data,
        "measurement_type": "gain"
    })
    print(f"Result: {json.dumps(analysis_result, indent=2)}")
    
    print("\n✅ AI workflow demonstration complete!")
    print("\nThis shows how an AI model can:")
    print("- Discover available instruments")
    print("- Create complex test workflows")
    print("- Execute measurements")
    print("- Analyze results and provide insights")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_ai_workflow())