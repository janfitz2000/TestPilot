from typing import Dict, Any, List, Optional
import logging
import os
import google.generativeai as genai

from .config import settings

logger = logging.getLogger(__name__)

class AIClient:
    """AI client for handling various AI operations"""
    
    def __init__(self):
        self.gemini_client = None
        
        # Initialize Google Gemini client if API key is provided
        google_api_key = settings.google_api_key or os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI client initialized")
        else:
            logger.warning("No Google API key found, using fallback responses")
    
    async def generate_test_plan(
        self,
        description: str,
        context: List[str],
        instruments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate test plan from natural language description"""
        
        system_prompt = """You are an expert test automation engineer specializing in electronic lab equipment. 
        Generate detailed test plans from natural language descriptions.
        
        Context from instrument manuals:
        {context}
        
        Available instruments: {instruments}
        
        IMPORTANT: If the user asks for an "IV curve" or "I-V curve" test, create a test plan for measuring current vs voltage characteristics of the device. This requires:
        - DC power supply for voltage sweep
        - Current measurement capability (DMM or parametric analyzer)
        - Voltage sweep from 0V to maximum operating voltage
        - Current measurement at each voltage point
        - Plotting I-V characteristics
        
        Return a structured test plan with:
        **Test Objectives:**
        • [List 3-4 specific objectives]
        
        **Required Instruments:**
        • [List specific instruments needed]
        
        **Test Procedures:**
        1. [Detailed step-by-step procedures]
        
        **Expected Results:**
        [Description of expected outcomes]
        
        **Pass/Fail Criteria:**
        [Specific criteria for success]
        
        Use bullet points and numbered lists for clarity.
        """
        
        user_prompt = f"""Generate a test plan for: {description}"""
        
        try:
            if self.gemini_client:
                logger.info(f"Using Gemini AI to generate test plan for: {description}")
                response = await self._call_gemini(system_prompt, user_prompt, context, instruments)
                logger.info(f"Gemini response received: {len(response.get('raw_response', '')) if response else 0} characters")
                return response
            else:
                logger.warning("No Gemini client available, using enhanced fallback")
                # Fallback to enhanced mock response for development
                response = self._generate_enhanced_test_plan(description, instruments)
                return response
        except Exception as e:
            logger.error(f"Failed to generate test plan with Gemini: {e}")
            logger.info("Falling back to enhanced test plan generation")
            return self._generate_enhanced_test_plan(description, instruments)
    
    async def optimize_parameters(
        self,
        current_params: Dict[str, Any],
        objective: str,
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Optimize test parameters using AI"""
        
        # Placeholder implementation
        optimized_params = current_params.copy()
        
        # Mock optimization - in reality, this would use ML models
        for key, value in current_params.items():
            if isinstance(value, (int, float)):
                optimized_params[key] = value * 0.95  # Mock 5% improvement
        
        return optimized_params
    
    async def analyze_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test failure and provide suggestions"""
        
        # Placeholder implementation
        return {
            "root_cause": "Parameter out of range",
            "suggestions": [
                "Check instrument calibration",
                "Verify test setup",
                "Review environmental conditions"
            ],
            "confidence": 0.75
        }
    
    async def _call_gemini(self, system_prompt: str, user_prompt: str, context: List[str], instruments: List[str]) -> Dict[str, Any]:
        """Call Google Gemini API"""
        try:
            # Combine system prompt and user prompt for Gemini
            full_prompt = system_prompt.format(
                context="\n".join(context) if context else "No additional context",
                instruments=", ".join(instruments) if instruments else "Auto-detect instruments"
            ) + "\n\n" + user_prompt + "\n\nPlease provide a detailed response with specific procedures, instruments, and SCPI commands."
            
            logger.info(f"Sending request to Gemini API with prompt length: {len(full_prompt)}")
            
            # Use asyncio to run the sync API call in a thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.ai_temperature,
                        max_output_tokens=settings.ai_max_tokens,
                    )
                )
            )
            
            logger.info(f"Gemini API response received: {len(response.text)} characters")
            logger.debug(f"Gemini raw response: {response.text[:200]}...")
            
            return self._parse_test_plan_response(response.text)
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    
    def _parse_test_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured test plan"""
        try:
            # Try to extract structured information from AI response
            lines = response.split('\n')
            
            # Initialize with defaults
            objectives = []
            instruments = []
            procedures = []
            expected_results = "All measurements within specification"
            pass_criteria = "< 5% deviation from nominal values"
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect sections
                if any(keyword in line.lower() for keyword in ['objective', 'goal', 'purpose']):
                    current_section = 'objectives'
                elif any(keyword in line.lower() for keyword in ['instrument', 'equipment', 'hardware']):
                    current_section = 'instruments'
                elif any(keyword in line.lower() for keyword in ['procedure', 'step', 'method', 'process']):
                    current_section = 'procedures'
                elif any(keyword in line.lower() for keyword in ['expected', 'result', 'output']):
                    current_section = 'expected_results'
                elif any(keyword in line.lower() for keyword in ['pass', 'criteria', 'threshold']):
                    current_section = 'pass_criteria'
                elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    # Bullet point - add to current section
                    item = line[1:].strip()
                    if current_section == 'objectives':
                        objectives.append(item)
                    elif current_section == 'instruments':
                        instruments.append(item)
                    elif current_section == 'procedures':
                        procedures.append(item)
                elif line[0].isdigit() and '.' in line[:3]:
                    # Numbered list item
                    item = line.split('.', 1)[1].strip()
                    if current_section == 'procedures':
                        procedures.append(item)
            
            # If nothing was extracted, use intelligent defaults based on response content
            if not objectives:
                if 'iv' in response.lower() or 'current' in response.lower():
                    objectives = ["Measure I-V characteristics", "Characterize amplifier linearity", "Determine operating point"]
                else:
                    objectives = ["Verify device functionality", "Characterize performance parameters"]
            
            if not instruments:
                if 'iv' in response.lower() or 'current' in response.lower():
                    instruments = ["DC Power Supply", "Digital Multimeter", "Parametric Analyzer", "Oscilloscope"]
                else:
                    instruments = ["Signal Generator", "Spectrum Analyzer", "Power Meter"]
            
            if not procedures:
                if 'iv' in response.lower() or 'current' in response.lower():
                    procedures = [
                        "Configure DC power supply for voltage sweep",
                        "Set current measurement range",
                        "Execute voltage sweep from minimum to maximum",
                        "Record current at each voltage point",
                        "Plot I-V curve and analyze linearity",
                        "Determine key parameters (threshold, transconductance)"
                    ]
                else:
                    procedures = [
                        "Initialize and configure test equipment",
                        "Establish baseline measurements",
                        "Execute test sequence",
                        "Analyze results"
                    ]
            
            return {
                "objectives": objectives,
                "instruments": instruments,
                "procedures": procedures,
                "expected_results": expected_results,
                "pass_criteria": pass_criteria,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            # Fallback to simple parsing
            return {
                "objectives": ["Parse and execute test plan"],
                "instruments": ["Auto-detected instruments"],
                "procedures": ["Execute AI-generated procedure"],
                "expected_results": "Test completion",
                "pass_criteria": "All steps completed successfully",
                "raw_response": response
            }
    
    def _generate_enhanced_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate enhanced test plan based on description"""
        desc_lower = description.lower()
        
        # Determine test type and generate appropriate plan
        if any(keyword in desc_lower for keyword in ["amplifier", "rf", "wifi", "radio"]):
            return self._generate_rf_test_plan(description, instruments)
        elif any(keyword in desc_lower for keyword in ["power", "supply", "voltage"]):
            return self._generate_power_test_plan(description, instruments)
        elif any(keyword in desc_lower for keyword in ["oscilloscope", "scope", "waveform"]):
            return self._generate_scope_test_plan(description, instruments)
        elif any(keyword in desc_lower for keyword in ["frequency", "sweep", "response"]):
            return self._generate_frequency_test_plan(description, instruments)
        else:
            return self._generate_generic_test_plan(description, instruments)
    
    def _generate_rf_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate RF amplifier test plan"""
        return {
            "objectives": [
                "Measure amplifier gain vs frequency",
                "Characterize harmonic distortion",
                "Validate power handling capability",
                "Verify efficiency and linearity"
            ],
            "instruments": instruments or ["Signal Generator", "Spectrum Analyzer", "Power Meter", "Network Analyzer"],
            "procedures": [
                "System initialization and calibration",
                "Configure signal generator for 2.4GHz operation",
                "Set up spectrum analyzer for harmonic analysis",
                "Perform frequency sweep measurements",
                "Execute power compression analysis",
                "Temperature monitoring and thermal analysis"
            ],
            "expected_results": "Gain: 18-22 dB, Harmonics: <-40 dBc, Efficiency: >75%",
            "pass_criteria": "All measurements within specification limits",
            "raw_response": f"RF test plan generated for: {description}"
        }
    
    def _generate_power_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate power supply test plan"""
        return {
            "objectives": [
                "Verify output voltage regulation",
                "Measure load transient response",
                "Characterize ripple and noise",
                "Validate current limiting"
            ],
            "instruments": instruments or ["Digital Multimeter", "Electronic Load", "Oscilloscope", "Spectrum Analyzer"],
            "procedures": [
                "Connect power supply to test load",
                "Configure output voltage and current limits",
                "Perform load regulation testing",
                "Measure ripple and noise characteristics",
                "Test transient response and recovery",
                "Verify protection mechanisms"
            ],
            "expected_results": "Regulation: <1%, Ripple: <50mV, Response: <100μs",
            "pass_criteria": "All parameters within datasheet specifications",
            "raw_response": f"Power supply test plan generated for: {description}"
        }
    
    def _generate_scope_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate oscilloscope test plan"""
        return {
            "objectives": [
                "Measure signal timing parameters",
                "Analyze waveform characteristics",
                "Capture and analyze transients",
                "Verify signal integrity"
            ],
            "instruments": instruments or ["Oscilloscope", "Function Generator", "Probe Station"],
            "procedures": [
                "Configure oscilloscope channels and triggering",
                "Set appropriate time base and voltage scales",
                "Capture representative waveforms",
                "Measure rise/fall times and delays",
                "Analyze frequency domain characteristics",
                "Document measurement results"
            ],
            "expected_results": "Clean signals with proper timing relationships",
            "pass_criteria": "Timing within ±5% of nominal values",
            "raw_response": f"Oscilloscope test plan generated for: {description}"
        }
    
    def _generate_frequency_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate frequency response test plan"""
        return {
            "objectives": [
                "Characterize frequency response",
                "Measure bandwidth and roll-off",
                "Analyze phase characteristics",
                "Validate filter performance"
            ],
            "instruments": instruments or ["Network Analyzer", "Signal Generator", "Spectrum Analyzer"],
            "procedures": [
                "Calibrate network analyzer",
                "Configure frequency sweep parameters",
                "Perform S-parameter measurements",
                "Analyze magnitude and phase response",
                "Extract key performance metrics",
                "Generate frequency response plots"
            ],
            "expected_results": "Flat response in passband, sharp roll-off",
            "pass_criteria": "±1 dB ripple, >40 dB stopband rejection",
            "raw_response": f"Frequency response test plan generated for: {description}"
        }
    
    def _generate_generic_test_plan(self, description: str, instruments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate generic test plan"""
        return {
            "objectives": [f"Execute comprehensive testing for: {description}"],
            "instruments": instruments or ["Multimeter", "Signal Generator", "Oscilloscope"],
            "procedures": [
                "Initialize and configure test equipment",
                "Establish baseline measurements",
                "Execute primary test sequence",
                "Collect and validate measurement data",
                "Perform statistical analysis",
                "Generate test report and documentation"
            ],
            "expected_results": "All measurements within acceptable ranges",
            "pass_criteria": "Meets design specifications and requirements",
            "raw_response": f"Generic test plan generated for: {description}"
        }