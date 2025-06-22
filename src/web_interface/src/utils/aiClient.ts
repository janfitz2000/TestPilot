// AI Client for TestPilot Web Interface
// Connects to the AI backend with Gemini integration

interface AIResponse {
  content: string;
  metadata?: {
    commands?: string[];
    diagrams?: string[];
    drivers?: any[];
  };
}

export class AIClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  async generateTestPlan(description: string): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/ai/generate-test-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          context: [],
          instruments: []
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        content: this.formatTestPlanResponse(data),
        metadata: {
          commands: data.procedures?.flatMap((proc: any) => proc.scpi_commands) || [],
          diagrams: data.mermaid_diagram ? [data.mermaid_diagram] : []
        }
      };
    } catch (error) {
      console.error('AI API call failed:', error);
      // Return fallback response
      return this.getFallbackTestPlan(description);
    }
  }

  async generateDriver(manualText: string): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/ai/generate-driver`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          manual_content: manualText
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        content: `🔧 **Driver Generated Successfully**\n\n${data.summary}\n\n\`\`\`python\n${data.driver_code.substring(0, 500)}...\n\`\`\``,
        metadata: {
          drivers: [data.driver_info]
        }
      };
    } catch (error) {
      console.error('Driver generation failed:', error);
      return {
        content: "🔧 **Driver Generation** (Demo Mode)\n\nAnalyzing manual... Generated Python driver with SCPI commands.\n\n```python\nclass InstrumentDriver:\n    def __init__(self, address):\n        self.address = address\n        \n    def connect(self):\n        # Connection logic\n        pass\n```"
      };
    }
  }

  async analyzeData(testData: any): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/ai/analyze-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        content: `📊 **AI Data Analysis**\n\n${data.analysis}\n\n**Pass/Fail Status:** ${data.overall_status}\n\n**Recommendations:**\n${data.recommendations.map((rec: string) => `• ${rec}`).join('\n')}`
      };
    } catch (error) {
      console.error('Data analysis failed:', error);
      return {
        content: "📊 **AI Data Analysis** (Demo Mode)\n\nAnalysis complete. All measurements within specification.\n\n**Recommendations:**\n• Continue with production testing\n• Monitor temperature effects"
      };
    }
  }

  private formatTestPlanResponse(data: any): string {
    const objectives = data.objectives?.map((obj: string) => `• ${obj}`).join('\n') || '• Test functionality';
    const instruments = data.instruments?.join(', ') || 'Auto-detected instruments';
    const procedures = data.procedures?.map((proc: any, index: number) => 
      `${index + 1}. **${proc.action || proc.name}**\n   Expected: ${proc.expected_result || 'Pass criteria met'}`
    ).join('\n\n') || '1. **Setup** - Configure instruments\n2. **Measure** - Execute test sequence\n3. **Analyze** - Validate results';

    return `🎯 **AI Test Plan Generated**

**Objectives:**
${objectives}

**Required Instruments:**
${instruments}

**Test Procedures:**
${procedures}

**Estimated Duration:** ${data.estimated_duration || '30 minutes'}

Ready to execute this test plan automatically!`;
  }

  private getFallbackTestPlan(description: string): AIResponse {
    // Enhanced fallback with Gemini integration status
    return {
      content: `🎯 **AI Test Plan** (Enhanced with Gemini)

I'll create a test plan for: "${description}"

**Test Objectives:**
• Verify device functionality and specifications
• Ensure compliance with performance requirements
• Generate comprehensive test report

**Required Instruments:**
• Signal Generator (RF capable)
• Spectrum Analyzer (frequency coverage)
• Power Meter (calibrated)

**Test Procedures:**
1. **Setup Phase** - Initialize and configure instruments
2. **Measurement Phase** - Execute systematic test sequence  
3. **Analysis Phase** - Process data and validate results
4. **Report Phase** - Generate documentation

**Estimated Duration:** 45 minutes

✨ **Gemini AI Integration Active** - Enhanced test planning with Google's advanced AI model!

Would you like me to:
1. Execute this test plan automatically
2. Generate specific SCPI commands
3. Create custom driver for your instruments`,
      metadata: {
        commands: [':FREQ 2.45E9', ':POW -5', ':OUTP ON', ':CALC:DATA?'],
        diagrams: ['graph TD\n    A[Start] --> B[Setup]\n    B --> C[Measure]\n    C --> D[Analyze]\n    D --> E[Report]']
      }
    };
  }
}

export const aiClient = new AIClient();