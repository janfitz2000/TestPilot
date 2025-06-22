use anyhow::{anyhow, Result};
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::time::timeout;
use tracing::{debug, info};

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

    pub async fn ensure_connected(&mut self) -> Result<()> {
        if self.stream.is_none() {
            let addr = format!("{}:{}", self.address, self.port);
            let stream = timeout(Duration::from_secs(5), TcpStream::connect(&addr)).await??;
            self.stream = Some(stream);
        }
        Ok(())
    }
}

#[async_trait::async_trait]
impl InstrumentConnection for ScpiClient {
    async fn connect(&self) -> Result<()> {
        // No-op: connection is managed in ensure_connected
        Ok(())
    }

    async fn disconnect(&self) -> Result<()> {
        // Drop the stream to disconnect
        // (In practice, you may want to implement a close method)
        Ok(())
    }

    async fn send_command(&mut self, command: &str) -> Result<String> {
        self.ensure_connected().await?;
        let stream = self.stream.as_mut().ok_or_else(|| anyhow!("Not connected"))?;
        let command_with_terminator = if command.ends_with('\n') {
            command.to_string()
        } else {
            format!("{}\n", command)
        };
        stream.write_all(command_with_terminator.as_bytes()).await?;
        if command.trim().ends_with('?') {
            let mut buffer = Vec::new();
            let mut temp_buffer = [0; 1024];
            loop {
                let n = stream.read(&mut temp_buffer).await?;
                if n == 0 {
                    break;
                }
                buffer.extend_from_slice(&temp_buffer[..n]);
                if buffer.ends_with(b"\n") {
                    break;
                }
            }
            let response = String::from_utf8_lossy(&buffer).trim().to_string();
            Ok(response)
        } else {
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