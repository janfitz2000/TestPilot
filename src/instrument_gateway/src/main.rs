use axum::{
    debug_handler,
    extract::{Path, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::cors::CorsLayer;
use tracing::{info, error};
use uuid::Uuid;

mod instrument;
mod scpi;
mod config;
mod health;

use instrument::{Instrument, InstrumentManager};
use config::Config;

#[derive(Clone)]
pub struct AppState {
    pub instrument_manager: Arc<RwLock<InstrumentManager>>,
    pub config: Arc<Config>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InstrumentResponse {
    pub id: Uuid,
    pub name: String,
    pub instrument_type: String,
    pub address: String,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateInstrumentRequest {
    pub name: String,
    pub r#type: String, // using r#type since type is a keyword
    pub address: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandRequest {
    pub command: String,
    pub timeout_ms: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandResponse {
    pub response: Option<String>,
    pub success: bool,
    pub error: Option<String>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Load configuration
    let config = Arc::new(Config::load()?);
    
    // Initialize instrument manager
    let instrument_manager = Arc::new(RwLock::new(InstrumentManager::new()));
    
    let state = AppState {
        instrument_manager,
        config,
    };

    // Build routes
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health::health_check))
        .route("/instruments", get(list_instruments).post(create_instrument))
        .route("/instruments/:id", get(get_instrument))
        .route("/instruments/:id/command", post(send_command))
        .route("/instruments/:id/connect", post(connect_instrument))
        .route("/instruments/:id/disconnect", post(disconnect_instrument))
        .route("/metrics", get(metrics))
        .layer(CorsLayer::permissive())
        .with_state(state);

    // Start server
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await?;
    info!("Instrument Gateway listening on 0.0.0.0:8000");
    
    axum::serve(listener, app).await?;
    Ok(())
}

#[debug_handler]
async fn root() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "TestPilot Instrument Gateway",
        "version": "1.0.0",
        "status": "running"
    }))
}

#[debug_handler]
async fn list_instruments(
    State(state): State<AppState>
) -> Result<Json<Vec<InstrumentResponse>>, StatusCode> {
    let manager = state.instrument_manager.read().await;
    let instruments: Vec<InstrumentResponse> = manager
        .list_instruments().await
        .into_iter()
        .map(|instrument| InstrumentResponse {
            id: instrument.id,
            name: instrument.name.clone(),
            instrument_type: instrument.instrument_type.clone(),
            address: instrument.address.clone(),
            status: if instrument.is_connected { "connected".to_string() } else { "disconnected".to_string() },
        })
        .collect();
    
    Ok(Json(instruments))
}

#[debug_handler]
async fn get_instrument(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<InstrumentResponse>, StatusCode> {
    let manager = state.instrument_manager.read().await;
    if let Some(instrument) = manager.get_instrument(&id).await {
        Ok(Json(InstrumentResponse {
            id: instrument.id,
            name: instrument.name.clone(),
            instrument_type: instrument.instrument_type.clone(),
            address: instrument.address.clone(),
            status: if instrument.is_connected { "connected".to_string() } else { "disconnected".to_string() },
        }))
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}

#[debug_handler]
async fn create_instrument(
    State(state): State<AppState>,
    Json(payload): Json<CreateInstrumentRequest>,
) -> Result<Json<InstrumentResponse>, StatusCode> {
    let manager = state.instrument_manager.write().await;
    let instrument = Instrument::new(
        payload.name,
        payload.r#type,
        payload.address,
    );
    let response = InstrumentResponse {
        id: instrument.id,
        name: instrument.name.clone(),
        instrument_type: instrument.instrument_type.clone(),
        address: instrument.address.clone(),
        status: "disconnected".to_string(),
    };
    manager.add_instrument(instrument).await;
    Ok(Json(response))
}

#[debug_handler]
async fn connect_instrument(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let manager = state.instrument_manager.write().await;
    match manager.connect_instrument(&id).await {
        Ok(_) => Ok(Json(serde_json::json!({"status": "connected"}))),
        Err(e) => {
            error!("Failed to connect instrument {}: {}", id, e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

#[debug_handler]
async fn disconnect_instrument(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let manager = state.instrument_manager.write().await;
    match manager.disconnect_instrument(&id).await {
        Ok(_) => Ok(Json(serde_json::json!({"status": "disconnected"}))),
        Err(e) => {
            error!("Failed to disconnect instrument {}: {}", id, e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

#[debug_handler]
async fn send_command(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
    Json(payload): Json<CommandRequest>,
) -> Result<Json<CommandResponse>, StatusCode> {
    let manager = state.instrument_manager.write().await;
    match manager.send_command(&id, &payload.command).await {
        Ok(response) => Ok(Json(CommandResponse {
            response: Some(response),
            success: true,
            error: None,
        })),
        Err(e) => {
            error!("Command failed for instrument {}: {}", id, e);
            Ok(Json(CommandResponse {
                response: None,
                success: false,
                error: Some(e.to_string()),
            }))
        }
    }
}

async fn metrics() -> String {
    // Placeholder for Prometheus metrics
    "# HELP instrument_gateway_requests_total Total number of requests\n".to_string()
}