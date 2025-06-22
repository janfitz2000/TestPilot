import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, Cpu, Zap, Wrench } from 'lucide-react';
import mermaid from 'mermaid';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    commands?: string[];
    diagrams?: string[];
    drivers?: DriverInfo[];
    test_plan_id?: string;
    can_execute?: boolean;
    execution_id?: string;
  };
}

interface DriverInfo {
  name: string;
  manufacturer: string;
  model: string;
  capabilities: string[];
  commands: number;
  generated_date: string;
}

interface TestFlow {
  name: string;
  steps: TestStep[];
  estimated_time: string;
  instruments: string[];
}

interface TestStep {
  id: string;
  name: string;
  type: 'setup' | 'measurement' | 'analysis' | 'report';
  duration: string;
  dependencies: string[];
  commands: string[];
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: '🤖 TestPilot AI Assistant ready! I can help you with:\n\n• Generate test plans from natural language\n• Create custom instrument drivers\n• Design test flow diagrams\n• Execute SCPI commands\n• Analyze measurement data\n\nWhat would you like to test today?',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentDiagram, setCurrentDiagram] = useState<string | null>(null);
  const [showDiagramPanel, setShowDiagramPanel] = useState(false);
  const [availableDrivers, setAvailableDrivers] = useState<DriverInfo[]>([
    {
      name: "Keysight E5071C Driver",
      manufacturer: "Keysight", 
      model: "E5071C",
      capabilities: ["S-Parameters", "Network Analysis", "Calibration"],
      commands: 45,
      generated_date: "2024-01-15"
    },
    {
      name: "Rigol DSO1104Z Driver",
      manufacturer: "Rigol",
      model: "DSO1104Z", 
      capabilities: ["Oscilloscope", "Waveform Capture", "Triggering"],
      commands: 32,
      generated_date: "2024-01-14"
    }
  ]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Initialize mermaid with proper configuration
    mermaid.initialize({ 
      startOnLoad: false,  // We'll render manually
      theme: 'neutral',
      securityLevel: 'loose',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true
      },
      themeVariables: {
        primaryColor: '#3b82f6',
        primaryTextColor: '#1f2937',
        primaryBorderColor: '#1d4ed8',
        lineColor: '#6b7280'
      }
    });
  }, []);

  // Helper functions for AI response processing
  const extractSCPICommands = (text: string): string[] => {
    const scpiPattern = /[:*][A-Z][A-Z0-9:?]*(?:\s+[^\s]+)?/g;
    const matches = text.match(scpiPattern) || [];
    return matches.slice(0, 10); // Limit to 10 commands
  };

  const extractMermaidDiagrams = (text: string): string[] => {
    const mermaidPattern = /```mermaid\s*([\s\S]*?)\s*```/g;
    const diagrams = [];
    let match;
    while ((match = mermaidPattern.exec(text)) !== null) {
      diagrams.push(match[1].trim());
    }
    return diagrams;
  };

  // Auto-render mermaid diagrams when messages change
  useEffect(() => {
    const renderDiagrams = async () => {
      for (const message of messages) {
        if (message.type === 'assistant' && message.content.includes('```mermaid')) {
          const diagrams = extractMermaidDiagrams(message.content);
          for (let diagramIndex = 0; diagramIndex < diagrams.length; diagramIndex++) {
            const diagram = diagrams[diagramIndex];
            const elementId = `mermaid-${message.id}-${diagramIndex}`;
            // Wait a bit to ensure DOM is ready
            await new Promise(resolve => setTimeout(resolve, 200));
            await renderMermaidDiagram(diagram, elementId);
          }
        }
      }
    };
    
    renderDiagrams();
  }, [messages]);

  // Render diagram in panel when currentDiagram changes
  useEffect(() => {
    if (currentDiagram && showDiagramPanel) {
      const renderPanelDiagram = async () => {
        await new Promise(resolve => setTimeout(resolve, 300)); // Wait for panel animation
        await renderMermaidDiagram(currentDiagram, 'diagram-panel');
      };
      renderPanelDiagram();
    }
  }, [currentDiagram, showDiagramPanel]);

  const generateMermaidDiagram = (testFlow: TestFlow): string => {
    const mermaidCode = `
graph TD
    Start([Start Test]) --> Setup{Setup Phase}
    
    ${testFlow.steps.map((step, index) => {
      const stepId = `Step${index + 1}`;
      const nextStepId = index < testFlow.steps.length - 1 ? `Step${index + 2}` : 'End';
      
      let shape = '';
      switch (step.type) {
        case 'setup':
          shape = `${stepId}[🔧 ${step.name}]`;
          break;
        case 'measurement':
          shape = `${stepId}(📊 ${step.name})`;
          break;
        case 'analysis':
          shape = `${stepId}{🧠 ${step.name}}`;
          break;
        case 'report':
          shape = `${stepId}[📄 ${step.name}]`;
          break;
        default:
          shape = `${stepId}[${step.name}]`;
      }
      
      return `
    Setup --> ${stepId}
    ${shape}
    ${stepId} --> ${nextStepId}`;
    }).join('')}
    
    Step${testFlow.steps.length} --> End([Test Complete])
    
    classDef setupClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef measureClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef analysisClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef reportClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class ${testFlow.steps.filter(s => s.type === 'setup').map((_, i) => `Step${testFlow.steps.findIndex(s => s.type === 'setup') + i + 1}`).join(',')} setupClass
    class ${testFlow.steps.filter(s => s.type === 'measurement').map((_, i) => `Step${testFlow.steps.findIndex(s => s.type === 'measurement') + i + 1}`).join(',')} measureClass
    class ${testFlow.steps.filter(s => s.type === 'analysis').map((_, i) => `Step${testFlow.steps.findIndex(s => s.type === 'analysis') + i + 1}`).join(',')} analysisClass
    class ${testFlow.steps.filter(s => s.type === 'report').map((_, i) => `Step${testFlow.steps.findIndex(s => s.type === 'report') + i + 1}`).join(',')} reportClass
    `;
    
    return mermaidCode.trim();
  };

  const renderMermaidDiagram = async (mermaidCode: string, elementId: string) => {
    try {
      const element = document.getElementById(elementId);
      if (element) {
        element.innerHTML = '<div class="text-center text-gray-500">🔄 Rendering diagram...</div>';
        
        // Clean up the mermaid code
        const cleanCode = mermaidCode.trim().replace(/^\s*graph\s+/i, 'graph ');
        
        // Use the newer mermaid API
        const { svg, bindFunctions } = await mermaid.render(`diagram-${elementId}`, cleanCode);
        element.innerHTML = svg;
        
        // Bind any interactive functions if needed
        if (bindFunctions) {
          bindFunctions(element);
        }
      }
    } catch (error) {
      console.error('Mermaid rendering error:', error);
      const element = document.getElementById(elementId);
      if (element) {
        element.innerHTML = `<div class="text-center text-red-500 p-4 border border-red-200 rounded">
          ❌ Diagram rendering failed<br>
          <small class="text-gray-500">Check console for details</small>
        </div>`;
      }
    }
  };

  const processAIResponse = async (userMessage: string): Promise<Message> => {
    try {
      // Call real AI orchestrator backend
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          context: []
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('AI Response:', data);
        
        // Show diagram in side panel if available
        if (data.metadata?.mermaid_diagram) {
          setCurrentDiagram(data.metadata.mermaid_diagram);
          setShowDiagramPanel(true);
        }

        return {
          id: Date.now().toString(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          metadata: {
            commands: data.metadata?.scpi_commands || extractSCPICommands(data.response),
            diagrams: data.metadata?.mermaid_diagram ? [data.metadata.mermaid_diagram] : extractMermaidDiagrams(data.response),
            test_plan_id: data.metadata?.test_plan_id,
            can_execute: data.metadata?.can_execute || false
          }
        };
      }
    } catch (error) {
      console.error('AI backend not available, using fallback:', error);
    }

    // Fallback to enhanced mock responses if backend unavailable
    const lowerInput = userMessage.toLowerCase();
    
    if (lowerInput.includes('test') && (lowerInput.includes('amplifier') || lowerInput.includes('rf') || lowerInput.includes('wifi'))) {
      // Generate test plan response
      const testFlow: TestFlow = {
        name: "WiFi Amplifier Characterization",
        estimated_time: "45 minutes",
        instruments: ["Signal Generator", "Spectrum Analyzer", "Power Meter"],
        steps: [
          {
            id: "1",
            name: "Initialize Instruments",
            type: "setup",
            duration: "5 min",
            dependencies: [],
            commands: ["*RST", ":OUTP ON", ":FREQ 2.45E9"]
          },
          {
            id: "2", 
            name: "Gain vs Frequency",
            type: "measurement",
            duration: "15 min",
            dependencies: ["1"],
            commands: [":FREQ:STAR 2.4E9", ":FREQ:STOP 2.5E9", ":SWE:POIN 201"]
          },
          {
            id: "3",
            name: "Power Sweep",
            type: "measurement", 
            duration: "10 min",
            dependencies: ["2"],
            commands: [":POW:STAR -10", ":POW:STOP 10", ":SWE:TYPE POW"]
          },
          {
            id: "4",
            name: "Analyze Results",
            type: "analysis",
            duration: "10 min", 
            dependencies: ["3"],
            commands: [":CALC:DATA:FDAT?", ":CALC:MATH:FUNC GAIN"]
          },
          {
            id: "5",
            name: "Generate Report",
            type: "report",
            duration: "5 min",
            dependencies: ["4"],
            commands: [":MMEM:STOR:TRAC ALL", ":HCOP:DEST 'PDF'"]
          }
        ]
      };

      const mermaidCode = generateMermaidDiagram(testFlow);
      
      setTimeout(() => {
        renderMermaidDiagram(mermaidCode, `mermaid-${Date.now()}`);
      }, 100);

      return {
        id: Date.now().toString(),
        type: 'assistant',
        content: `🎯 **WiFi Amplifier Test Plan Generated**

I've created a comprehensive test plan for your WiFi amplifier:

**Test Objectives:**
• Measure gain vs frequency (2.4-2.5 GHz)
• Characterize power handling and compression
• Validate specifications and generate report

**Required Instruments:**
• Signal Generator (2.4-2.5 GHz capable)
• Spectrum Analyzer (up to 6 GHz for harmonics)  
• Power Meter (calibrated at 2.4 GHz)

**Test Flow Diagram:**

<div id="mermaid-${Date.now()}" class="mermaid-diagram"></div>

**SCPI Commands Preview:**
\`\`\`
SIG_GEN: *RST; :OUTP ON; :FREQ 2.45E9
SPEC_AN: :FREQ:STAR 2.4E9; :FREQ:STOP 2.5E9  
PWR_MTR: :FREQ 2.45E9; :UNIT:POW DBM
\`\`\`

**Estimated Duration:** ${testFlow.estimated_time}

Would you like me to:
1. Execute this test plan automatically
2. Generate the complete SCPI command sequence
3. Create a custom driver for your specific instruments
4. Modify the test parameters`,
        timestamp: new Date(),
        metadata: {
          commands: testFlow.steps.flatMap(step => step.commands),
          diagrams: [mermaidCode]
        }
      };
    }
    
    else if (lowerInput.includes('driver') || lowerInput.includes('manual')) {
      return {
        id: Date.now().toString(),
        type: 'assistant',
        content: `🔧 **Custom Driver Generation**

I can generate Python drivers from instrument manuals! Here's what I need:

**Upload Options:**
• PDF manual file
• Text excerpt with SCPI commands
• Instrument model number for automatic lookup

**Driver Generation Process:**
1. 📄 Analyze manual content
2. 🔍 Extract SCPI commands and parameters  
3. 🏗️ Generate Python class structure
4. ✅ Add error handling and utilities
5. 📚 Create documentation and examples

**Current Driver Catalog:**

${availableDrivers.map(driver => `
**${driver.name}**
• Manufacturer: ${driver.manufacturer}
• Model: ${driver.model}  
• Commands: ${driver.commands}
• Capabilities: ${driver.capabilities.join(', ')}
• Generated: ${driver.generated_date}
`).join('')}

Would you like to:
1. Upload a manual to generate a new driver
2. Use an existing driver from the catalog
3. See the generated code for a specific driver`,
        timestamp: new Date(),
        metadata: {
          drivers: availableDrivers
        }
      };
    }
    
    else if (lowerInput.includes('diagram') || lowerInput.includes('flow') || lowerInput.includes('mermaid')) {
      const sampleFlow: TestFlow = {
        name: "Generic Test Flow",
        estimated_time: "30 minutes",
        instruments: ["Instrument A", "Instrument B"],
        steps: [
          { id: "1", name: "Setup", type: "setup", duration: "5 min", dependencies: [], commands: [] },
          { id: "2", name: "Measure", type: "measurement", duration: "15 min", dependencies: ["1"], commands: [] },
          { id: "3", name: "Analyze", type: "analysis", duration: "10 min", dependencies: ["2"], commands: [] }
        ]
      };

      const mermaidCode = generateMermaidDiagram(sampleFlow);
      setTimeout(() => {
        renderMermaidDiagram(mermaidCode, `mermaid-${Date.now()}`);
      }, 100);

      return {
        id: Date.now().toString(),
        type: 'assistant',
        content: `📊 **Test Flow Diagram Generator**

I can create Mermaid diagrams for your test flows! Here's a sample:

<div id="mermaid-${Date.now()}" class="mermaid-diagram"></div>

**Diagram Features:**
• 🔧 Setup steps (rectangles)
• 📊 Measurements (rounded rectangles)  
• 🧠 Analysis (diamonds)
• 📄 Reports (rectangles)

**Supported Diagram Types:**
• Test flow sequences
• Instrument connections
• Data flow diagrams
• System architecture

Describe your test flow and I'll generate a custom diagram!`,
        timestamp: new Date(),
        metadata: {
          diagrams: [mermaidCode]
        }
      };
    }
    
    else {
      return {
        id: Date.now().toString(),
        type: 'assistant',
        content: `🤖 I understand you want to: "${userMessage}"

I can help you with:

**🧪 Test Planning:**
• "Test a 2.4GHz amplifier gain and harmonics"
• "Characterize S-parameters of a filter"
• "Measure oscilloscope rise time"

**🔧 Driver Generation:**
• "Generate driver from manual"
• "Show available drivers"
• "Create driver for [instrument model]"

**📊 Diagram Creation:**
• "Create test flow diagram"
• "Show measurement sequence"
• "Generate system architecture"

**⚡ SCPI Commands:**
• Direct instrument control
• Command validation
• Automated sequences

Try asking me something like: *"Test a WiFi amplifier at 2.4GHz"* or *"Generate driver from manual"*`,
        timestamp: new Date()
      };
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await processAIResponse(input);
      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error('Error processing message:', error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'system',
        content: '❌ Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const executeTestPlan = async (testPlanId: string) => {
    try {
      console.log('Executing test plan:', testPlanId);
      
      const response = await fetch('http://localhost:8001/api/execute-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_plan_id: testPlanId,
          parameters: {}
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add execution status message
        const executionMessage: Message = {
          id: Date.now().toString(),
          type: 'system',
          content: `🚀 **Test Execution Started**\n\nExecution ID: ${data.execution_id}\n\nMonitoring test progress...`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, executionMessage]);
        
        // Start monitoring execution
        monitorExecution(data.execution_id);
      }
    } catch (error) {
      console.error('Test execution failed:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: `❌ **Test Execution Failed**\n\nError: ${error}\n\nPlease try again.`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const monitorExecution = async (executionId: string) => {
    let completed = false;
    
    while (!completed) {
      try {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
        
        const response = await fetch(`http://localhost:8001/api/executions/${executionId}`);
        
        if (response.ok) {
          const execution = await response.json();
          
          if (execution.status === 'completed') {
            completed = true;
            
            const completionMessage: Message = {
              id: Date.now().toString(),
              type: 'system',
              content: `✅ **Test Execution Completed**\n\nExecution ID: ${executionId}\nSteps Completed: ${execution.results.length}\nTotal Time: ${Math.round((new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()) / 1000)}s\n\n**Results:**\n${execution.results.map((result: any, i: number) => `${i+1}. ${result.name} - ${result.status} (${result.scpi_commands_executed} commands)`).join('\n')}`,
              timestamp: new Date()
            };
            
            setMessages(prev => [...prev, completionMessage]);
          } else if (execution.status === 'failed') {
            completed = true;
            
            const errorMessage: Message = {
              id: Date.now().toString(),
              type: 'system',
              content: `❌ **Test Execution Failed**\n\nExecution ID: ${executionId}\nError: ${execution.error}\n\nPlease check the test setup and try again.`,
              timestamp: new Date()
            };
            
            setMessages(prev => [...prev, errorMessage]);
          }
        }
      } catch (error) {
        console.error('Execution monitoring failed:', error);
        completed = true;
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const fileMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: `📄 Uploaded: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, fileMessage]);
      
      // Simulate file processing
      setTimeout(() => {
        const responseMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `✅ **File Analysis Complete**

Analyzed: ${file.name}

**Extracted Information:**
• Found 23 SCPI commands
• Identified instrument model and specs
• Generated Python driver class
• Added error handling and examples

**Generated Driver Preview:**
\`\`\`python
class InstrumentDriver:
    def __init__(self, address):
        self.address = address
        
    def connect(self):
        # Auto-generated connection code
        pass
        
    def get_identity(self):
        return self.query("*IDN?")
\`\`\`

Driver saved as: \`${file.name.replace(/\.[^/.]+$/, "")}_driver.py\`

Would you like to test the generated driver?`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, responseMessage]);
      }, 2000);
    }
  };

  return (
    <div className="flex h-full bg-white">
      {/* Main Chat Area */}
      <div className={`flex flex-col ${showDiagramPanel ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
        {/* Header */}
        <div className="flex-shrink-0 border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">TestPilot AI Assistant</h2>
              <p className="text-sm text-gray-500">Intelligent test automation and driver generation</p>
            </div>
            <div className="flex items-center space-x-4">
              {currentDiagram && (
                <button
                  onClick={() => setShowDiagramPanel(!showDiagramPanel)}
                  className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full hover:bg-blue-200 transition-colors"
                >
                  {showDiagramPanel ? 'Hide' : 'Show'} Diagram
                </button>
              )}
              <div className="flex items-center text-green-600">
                <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                <span className="text-sm">Online</span>
              </div>
            </div>
          </div>
        </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-4xl rounded-lg px-4 py-3 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'system'
                  ? 'bg-gray-100 text-gray-800'
                  : 'bg-gray-50 text-gray-900 border'
              }`}
            >
              <div className="whitespace-pre-wrap" dangerouslySetInnerHTML={{ 
                __html: message.content
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/• /g, '• ')
                  .replace(/```mermaid\s*([\s\S]*?)\s*```/g, (match, diagram, offset) => {
                    const diagramIndex = (message.content.substring(0, offset).match(/```mermaid/g) || []).length;
                    return `<div id="mermaid-${message.id}-${diagramIndex}" class="mermaid-diagram bg-white p-4 rounded border my-4" style="text-align: center;">🔄 Generating diagram...</div>`;
                  })
                  .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-800 text-green-400 p-3 rounded mt-2 overflow-x-auto"><code>$1</code></pre>')
                  .replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 rounded">$1</code>')
              }} />
              
              {message.metadata?.commands && (
                <div className="mt-3 p-3 bg-gray-800 rounded">
                  <div className="text-green-400 text-sm font-mono">
                    <div className="text-green-300 mb-2">SCPI Commands:</div>
                    {message.metadata.commands.slice(0, 5).map((cmd, i) => (
                      <div key={i} className="ml-2">• {cmd}</div>
                    ))}
                    {message.metadata.commands.length > 5 && (
                      <div className="ml-2 text-gray-400">... and {message.metadata.commands.length - 5} more</div>
                    )}
                  </div>
                </div>
              )}
              
              {message.metadata?.can_execute && message.metadata?.test_plan_id && (
                <div className="mt-3">
                  <button
                    onClick={() => executeTestPlan(message.metadata!.test_plan_id!)}
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
                  >
                    🚀 Execute Test Plan
                  </button>
                </div>
              )}
              
              <div className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 border rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.txt,.doc,.docx"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Upload manual or document"
          >
            <Upload className="w-5 h-5" />
          </button>
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to generate test plans, create drivers, or show diagrams..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            onClick={() => setInput("Test a 2.4GHz WiFi amplifier gain and harmonics")}
            className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors"
          >
            <Zap className="w-3 h-3 mr-1" />
            Test RF Amplifier
          </button>
          <button
            onClick={() => setInput("Generate driver from manual")}
            className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-100 text-green-800 hover:bg-green-200 transition-colors"
          >
            <Wrench className="w-3 h-3 mr-1" />
            Generate Driver
          </button>
          <button
            onClick={() => setInput("Create test flow diagram")}
            className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-purple-100 text-purple-800 hover:bg-purple-200 transition-colors"
          >
            <FileText className="w-3 h-3 mr-1" />
            Flow Diagram
          </button>
          <button
            onClick={() => setInput("Show available instrument drivers")}
            className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-orange-100 text-orange-800 hover:bg-orange-200 transition-colors"
          >
            <Cpu className="w-3 h-3 mr-1" />
            Driver Catalog
          </button>
        </div>
      </div>
    </div>
      
      {/* Diagram Panel */}
      {showDiagramPanel && currentDiagram && (
        <div className="w-1/3 border-l border-gray-200 bg-gray-50">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Test Flow Diagram</h3>
              <button
                onClick={() => setShowDiagramPanel(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>
          <div className="p-4 h-full overflow-auto">
            <div className="bg-white rounded-lg border p-4">
              <div 
                id="diagram-panel" 
                className="mermaid-diagram"
                style={{ minHeight: '400px', textAlign: 'center' }}
              >
                🔄 Rendering diagram...
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;