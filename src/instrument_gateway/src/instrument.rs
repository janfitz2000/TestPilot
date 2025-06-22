use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::time::{timeout, Duration};
use tracing::{error, info, warn};
use uuid::Uuid;

use crate::scpi::ScpiClient;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Instrument {
    pub id: Uuid,
    pub name: String,
    pub instrument_type: String,
    pub address: String,
    pub is_connected: bool,
    pub protocol: String,
    pub config: HashMap<String, String>,
}

impl Instrument {
    pub fn new(name: String, instrument_type: String, address: String) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            instrument_type,
            address,
            is_connected: false,
            protocol: "SCPI".to_string(),
            config: HashMap::new(),
        }
    }
}

pub struct InstrumentManager {
    pub instruments: HashMap<Uuid, Instrument>,
    pub connections: HashMap<Uuid, Box<dyn InstrumentConnection>>,
}

impl InstrumentManager {
    pub fn new() -> Self {
        Self {
            instruments: HashMap::new(),
            connections: HashMap::new(),
        }
    }

    pub fn add_instrument(&mut self, instrument: Instrument) {
        info!("Adding instrument: {} ({})", instrument.name, instrument.id);
        self.instruments.insert(instrument.id, instrument);
    }

    pub fn get_instrument(&self, id: &Uuid) -> Option<Instrument> {
        self.instruments.get(id).cloned()
    }

    pub fn list_instruments(&self) -> Vec<Instrument> {
        self.instruments.values().cloned().collect()
    }

    pub async fn connect_instrument(&mut self, id: &Uuid) -> Result<()> {
        let instrument = self.instruments.get_mut(id)
            .ok_or_else(|| anyhow!("Instrument not found"))?;

        if instrument.is_connected {
            return Ok(());
        }

        info!("Connecting to instrument: {}", instrument.name);

        // Create connection based on protocol
        let connection: Box<dyn InstrumentConnection> = match instrument.protocol.as_str() {
            "SCPI" => Box::new(ScpiClient::new(&instrument.address)?),
            _ => return Err(anyhow!("Unsupported protocol: {}", instrument.protocol)),
        };

        // Test connection
        match timeout(Duration::from_secs(5), connection.connect()).await {
            Ok(Ok(_)) => {
                instrument.is_connected = true;
                self.connections.insert(*id, connection);
                info!("Successfully connected to instrument: {}", instrument.name);
                Ok(())
            }
            Ok(Err(e)) => {
                error!("Failed to connect to instrument {}: {}", instrument.name, e);
                Err(e)
            }
            Err(_) => {
                error!("Connection timeout for instrument: {}", instrument.name);
                Err(anyhow!("Connection timeout"))
            }
        }
    }

    pub async fn disconnect_instrument(&mut self, id: &Uuid) -> Result<()> {
        let instrument = self.instruments.get_mut(id)
            .ok_or_else(|| anyhow!("Instrument not found"))?;

        if !instrument.is_connected {
            return Ok(());
        }

        info!("Disconnecting instrument: {}", instrument.name);

        if let Some(connection) = self.connections.remove(id) {
            if let Err(e) = connection.disconnect().await {
                warn!("Error during disconnect: {}", e);
            }
        }

        instrument.is_connected = false;
        info!("Disconnected instrument: {}", instrument.name);
        Ok(())
    }

    pub async fn send_command(&mut self, id: &Uuid, command: &str) -> Result<String> {
        let instrument = self.instruments.get(id)
            .ok_or_else(|| anyhow!("Instrument not found"))?;

        if !instrument.is_connected {
            return Err(anyhow!("Instrument not connected"));
        }

        let connection = self.connections.get_mut(id)
            .ok_or_else(|| anyhow!("No active connection"))?;

        info!("Sending command to {}: {}", instrument.name, command);

        match timeout(Duration::from_secs(10), connection.send_command(command)).await {
            Ok(Ok(response)) => {
                info!("Command response from {}: {}", instrument.name, response);
                Ok(response)
            }
            Ok(Err(e)) => {
                error!("Command failed for {}: {}", instrument.name, e);
                Err(e)
            }
            Err(_) => {
                error!("Command timeout for instrument: {}", instrument.name);
                Err(anyhow!("Command timeout"))
            }
        }
    }
}

#[async_trait::async_trait]
pub trait InstrumentConnection: Send + Sync {
    async fn connect(&self) -> Result<()>;
    async fn disconnect(&self) -> Result<()>;
    async fn send_command(&mut self, command: &str) -> Result<String>;
}