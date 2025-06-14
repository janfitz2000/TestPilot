use anyhow::{anyhow, Result};
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::time::timeout;
use tracing::{debug, error, info};

use crate::instrument::InstrumentConnection;

pub struct ScpiClient {
    address: String,
    port: u16,
    stream: Option<TcpStream>,
}

impl ScpiClient {
    pub fn new(address: &str) -> Result<Self> {
        // Parse address - format: IP:PORT or just IP (default to 5025)
        let (ip, port) = if address.contains(':') {
            let parts: Vec<&str> = address.split(':').collect();
            if parts.len() != 2 {
                return Err(anyhow!("Invalid address format: {}", address));
            }
            (parts[0].to_string(), parts[1].parse::<u16>()?)
        } else {
            (address.to_string(), 5025) // Default SCPI port
        };

        Ok(Self {
            address: ip,
            port,
            stream: None,
        })
    }
}

#[async_trait::async_trait]
impl InstrumentConnection for ScpiClient {
    async fn connect(&self) -> Result<()> {
        let addr = format!("{}:{}", self.address, self.port);
        info!("Connecting to SCPI instrument at {}", addr);
        
        // This is a simplified connection test
        // In reality, you'd store the connection for reuse
        match timeout(Duration::from_secs(5), TcpStream::connect(&addr)).await {
            Ok(Ok(_stream)) => {
                info!("Successfully connected to {}", addr);
                Ok(())
            }
            Ok(Err(e)) => {
                error!("Failed to connect to {}: {}", addr, e);
                Err(anyhow!("Connection failed: {}", e))
            }
            Err(_) => {
                error!("Connection timeout to {}", addr);
                Err(anyhow!("Connection timeout"))
            }
        }
    }

    async fn disconnect(&self) -> Result<()> {
        info!("Disconnecting from SCPI instrument");
        // Stream will be automatically closed when dropped
        Ok(())
    }

    async fn send_command(&mut self, command: &str) -> Result<String> {
        let addr = format!("{}:{}", self.address, self.port);
        debug!("Sending SCPI command to {}: {}", addr, command);

        // Create new connection for each command (simplified approach)
        let mut stream = match timeout(Duration::from_secs(5), TcpStream::connect(&addr)).await {
            Ok(Ok(stream)) => stream,
            Ok(Err(e)) => return Err(anyhow!("Failed to connect: {}", e)),
            Err(_) => return Err(anyhow!("Connection timeout")),
        };

        // Send command
        let command_with_terminator = if command.ends_with('\n') {
            command.to_string()
        } else {
            format!("{}\n", command)
        };

        if let Err(e) = stream.write_all(command_with_terminator.as_bytes()).await {
            return Err(anyhow!("Failed to send command: {}", e));
        }

        // Read response if it's a query (ends with ?)
        if command.trim().ends_with('?') {
            let mut buffer = Vec::new();
            let mut temp_buffer = [0; 1024];

            // Read response with timeout
            match timeout(Duration::from_secs(5), async {
                loop {
                    match stream.read(&mut temp_buffer).await {
                        Ok(0) => break, // Connection closed
                        Ok(n) => {
                            buffer.extend_from_slice(&temp_buffer[..n]);
                            // Check if we have a complete response (ends with newline)
                            if buffer.ends_with(b"\n") {
                                break;
                            }
                        }
                        Err(e) => return Err(anyhow!("Read error: {}", e)),
                    }
                }
                Ok::<(), anyhow::Error>(())
            }).await {
                Ok(Ok(_)) => {
                    let response = String::from_utf8_lossy(&buffer).trim().to_string();
                    debug!("SCPI response: {}", response);
                    Ok(response)
                }
                Ok(Err(e)) => Err(e),
                Err(_) => Err(anyhow!("Response timeout")),
            }
        } else {
            // Command without response
            Ok("OK".to_string())
        }
    }
}

// Mock SCPI client for testing
pub struct MockScpiClient {
    responses: std::collections::HashMap<String, String>,
}

impl MockScpiClient {
    pub fn new() -> Self {
        let mut responses = std::collections::HashMap::new();
        
        // Add some common SCPI responses
        responses.insert("*IDN?".to_string(), "Mock Instrument,Model123,Serial456,1.0.0".to_string());
        responses.insert("*OPC?".to_string(), "1".to_string());
        responses.insert(":SYST:ERR?".to_string(), "0,\"No error\"".to_string());
        
        Self { responses }
    }
}

#[async_trait::async_trait]
impl InstrumentConnection for MockScpiClient {
    async fn connect(&self) -> Result<()> {
        info!("Mock SCPI connection established");
        Ok(())
    }

    async fn disconnect(&self) -> Result<()> {
        info!("Mock SCPI connection closed");
        Ok(())
    }

    async fn send_command(&mut self, command: &str) -> Result<String> {
        debug!("Mock SCPI command: {}", command);
        
        if let Some(response) = self.responses.get(command.trim()) {
            Ok(response.clone())
        } else if command.trim().ends_with('?') {
            Ok("42.0".to_string()) // Generic numeric response
        } else {
            Ok("OK".to_string())
        }
    }
}