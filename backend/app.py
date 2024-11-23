from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for parking space data
parking_data = {
    "spaces": [],  # List of dictionaries with space status
    "total": 0,
    "free": 0,
    "occupied": 0,
}


# Data model for updating parking spaces
class ParkingUpdate(BaseModel):
    spaces: list  # List of space statuses (free/occupied)
    total: int
    free: int
    occupied: int


@app.get("/status")
def get_parking_status():
    """API to get the current parking lot status."""
    return parking_data


@app.post("/update")
def update_parking_status(update: ParkingUpdate):
    """API to update the parking lot status."""
    global parking_data
    print("Received data:", update.dict())  # Debugging log
    parking_data.update(update.dict())
    return {"message": "Parking data updated successfully"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    while True:
        await websocket.send_json(parking_data)
