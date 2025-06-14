from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TestPilot Instrument Gateway",
    description="Simple instrument communication service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for instruments
instruments_db: Dict[str, Dict[str, Any]] = {}

class InstrumentCreate(BaseModel):
    name: str
    type: str
    address: str
    protocol: str = "SCPI"

class InstrumentResponse(BaseModel):
    id: str
    name: str
    type: str
    address: str
    protocol: str
    connected: bool

class CommandRequest(BaseModel):
    command: str
    timeout: Optional[float] = 5.0

class CommandResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "service": "TestPilot Instrument Gateway",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "instruments": len(instruments_db)}

@app.get("/instruments", response_model=List[InstrumentResponse])
async def list_instruments():
    """List all instruments"""
    return [
        InstrumentResponse(
            id=inst_id,
            name=inst_data["name"],
            type=inst_data["type"],
            address=inst_data["address"],
            protocol=inst_data["protocol"],
            connected=inst_data.get("connected", False)
        )
        for inst_id, inst_data in instruments_db.items()
    ]

@app.post("/instruments", response_model=InstrumentResponse)
async def create_instrument(instrument: InstrumentCreate):
    """Add a new instrument"""
    import uuid
    inst_id = str(uuid.uuid4())
    
    instruments_db[inst_id] = {
        "name": instrument.name,
        "type": instrument.type,
        "address": instrument.address,
        "protocol": instrument.protocol,
        "connected": False
    }
    
    logger.info(f"Created instrument: {instrument.name} ({inst_id})")
    
    return InstrumentResponse(
        id=inst_id,
        name=instrument.name,
        type=instrument.type,
        address=instrument.address,
        protocol=instrument.protocol,
        connected=False
    )

@app.get("/instruments/{instrument_id}", response_model=InstrumentResponse)
async def get_instrument(instrument_id: str):
    """Get instrument details"""
    if instrument_id not in instruments_db:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    inst_data = instruments_db[instrument_id]
    return InstrumentResponse(
        id=instrument_id,
        name=inst_data["name"],
        type=inst_data["type"],
        address=inst_data["address"],
        protocol=inst_data["protocol"],
        connected=inst_data.get("connected", False)
    )

@app.post("/instruments/{instrument_id}/connect")
async def connect_instrument(instrument_id: str):
    """Connect to an instrument"""
    if instrument_id not in instruments_db:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    # Mock connection - in reality, you'd establish actual connection
    instruments_db[instrument_id]["connected"] = True
    logger.info(f"Connected to instrument: {instrument_id}")
    
    return {"status": "connected", "message": f"Connected to {instruments_db[instrument_id]['name']}"}

@app.post("/instruments/{instrument_id}/disconnect")
async def disconnect_instrument(instrument_id: str):
    """Disconnect from an instrument"""
    if instrument_id not in instruments_db:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    instruments_db[instrument_id]["connected"] = False
    logger.info(f"Disconnected from instrument: {instrument_id}")
    
    return {"status": "disconnected", "message": f"Disconnected from {instruments_db[instrument_id]['name']}"}

@app.post("/instruments/{instrument_id}/command", response_model=CommandResponse)
async def send_command(instrument_id: str, command: CommandRequest):
    """Send a command to an instrument"""
    if instrument_id not in instruments_db:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    inst_data = instruments_db[instrument_id]
    
    if not inst_data.get("connected", False):
        return CommandResponse(
            success=False,
            error="Instrument not connected"
        )
    
    logger.info(f"Sending command to {inst_data['name']}: {command.command}")
    
    # Mock SCPI command responses
    mock_responses = {
        "*IDN?": f"{inst_data['type']},TestPilot,SN123456,1.0.0",
        "*OPC?": "1",
        ":SYST:ERR?": "0,\"No error\"",
        ":MEAS:VOLT?": "3.14159",
        ":MEAS:CURR?": "0.001234",
        ":FREQ?": "1000000000.0",
        ":VOLT?": "5.0"
    }
    
    # Simulate command execution delay
    await asyncio.sleep(0.1)
    
    # Check if it's a query (ends with ?)
    if command.command.strip().endswith('?'):
        response = mock_responses.get(command.command.strip(), "42.0")
        return CommandResponse(success=True, response=response)
    else:
        # Command without response
        return CommandResponse(success=True, response="OK")

@app.delete("/instruments/{instrument_id}")
async def delete_instrument(instrument_id: str):
    """Delete an instrument"""
    if instrument_id not in instruments_db:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    inst_name = instruments_db[instrument_id]["name"]
    del instruments_db[instrument_id]
    logger.info(f"Deleted instrument: {inst_name} ({instrument_id})")
    
    return {"message": f"Instrument {inst_name} deleted successfully"}

# Initialize with some mock instruments
@app.on_event("startup")
async def startup_event():
    """Initialize with mock instruments"""
    mock_instruments = [
        {
            "name": "Keysight MSO-X 3104T",
            "type": "Oscilloscope",
            "address": "192.168.1.100",
            "protocol": "SCPI"
        },
        {
            "name": "Rigol DG4162", 
            "type": "Signal Generator",
            "address": "192.168.1.101",
            "protocol": "SCPI"
        },
        {
            "name": "Keysight B2900A",
            "type": "SMU", 
            "address": "192.168.1.102",
            "protocol": "SCPI"
        }
    ]
    
    import uuid
    for inst in mock_instruments:
        inst_id = str(uuid.uuid4())
        instruments_db[inst_id] = {**inst, "connected": False}
    
    logger.info(f"Initialized with {len(mock_instruments)} mock instruments")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)