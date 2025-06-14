use anyhow::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub server: ServerConfig,
    pub instruments: InstrumentConfig,
    pub messaging: MessagingConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstrumentConfig {
    pub default_timeout_ms: u64,
    pub max_connections: usize,
    pub connection_pool_size: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessagingConfig {
    pub nats_url: String,
    pub redis_url: String,
}

impl Config {
    pub fn load() -> Result<Self> {
        // Load from environment variables with defaults
        let config = Config {
            server: ServerConfig {
                host: std::env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
                port: std::env::var("PORT")
                    .unwrap_or_else(|_| "8000".to_string())
                    .parse()
                    .unwrap_or(8000),
            },
            instruments: InstrumentConfig {
                default_timeout_ms: std::env::var("INSTRUMENT_TIMEOUT_MS")
                    .unwrap_or_else(|_| "10000".to_string())
                    .parse()
                    .unwrap_or(10000),
                max_connections: std::env::var("MAX_CONNECTIONS")
                    .unwrap_or_else(|_| "100".to_string())
                    .parse()
                    .unwrap_or(100),
                connection_pool_size: std::env::var("CONNECTION_POOL_SIZE")
                    .unwrap_or_else(|_| "10".to_string())
                    .parse()
                    .unwrap_or(10),
            },
            messaging: MessagingConfig {
                nats_url: std::env::var("NATS_URL")
                    .unwrap_or_else(|_| "nats://localhost:4222".to_string()),
                redis_url: std::env::var("REDIS_URL")
                    .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            },
        };

        Ok(config)
    }
}