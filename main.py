from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class StatusChange(BaseModel):
    status: str
    startTime: str

class Machine(BaseModel):
    id: str
    statusChanges: List[StatusChange]
    currentStatus: str

def get_random_time(start: datetime, end: datetime) -> str:
    return (start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))).isoformat()

def generate_status_changes() -> List[StatusChange]:
    statuses = ['生產', '閒置', '當機', '裝機', '工程借機', '其他']
    changes = []
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    number_of_changes = random.randint(1, 7)

    for _ in range(number_of_changes):
        status = random.choice(statuses)
        start_time = get_random_time(start_of_day, now)
        changes.append(StatusChange(status=status, startTime=start_time))

    changes.sort(key=lambda x: x.startTime)

    if changes:
        changes[0].startTime = start_of_day.isoformat()

    return changes

@app.get("/api/machines", response_model=List[Machine])
async def get_machines():
    machines = []
    for i in range(100):
        status_changes = generate_status_changes()
        machine = Machine(
            id=f'{i+1:04d}',
            statusChanges=status_changes,
            currentStatus=status_changes[-1].status if status_changes else None
        )
        machines.append(machine)
    return machines

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)