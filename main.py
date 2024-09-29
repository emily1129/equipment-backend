from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random

SQLALCHEMY_DATABASE_URL = "postgresql://machineuser:realtek_machines@localhost/machinedb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# db models
class MachineDB(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True, index=True)
    current_status = Column(String)

class StatusChangeDB(Base):
    __tablename__ = "status_changes"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.id"))
    status = Column(String)
    start_time = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StatusChange(BaseModel):
    status: str
    startTime: str

class Machine(BaseModel):
    id: str
    statusChanges: List[StatusChange]
    currentStatus: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
async def get_machines(db: Session = Depends(get_db)):
    db_machines = db.query(MachineDB).all()
    machines = []
    for db_machine in db_machines:
        db_status_changes = db.query(StatusChangeDB).filter(StatusChangeDB.machine_id == db_machine.id).order_by(StatusChangeDB.start_time).all()
        status_changes = [StatusChange(status=sc.status, startTime=sc.start_time.isoformat()) for sc in db_status_changes]
        machine = Machine(
            id=db_machine.id,
            statusChanges=status_changes,
            currentStatus=db_machine.current_status
        )
        machines.append(machine)
    return machines
    
@app.get("/api/machines/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str, db: Session = Depends(get_db)):
    db_machine = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
    if db_machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    db_status_changes = db.query(StatusChangeDB).filter(StatusChangeDB.machine_id == machine_id).order_by(StatusChangeDB.start_time).all()
    status_changes = [StatusChange(status=sc.status, startTime=sc.start_time.isoformat()) for sc in db_status_changes]
    machine = Machine(
        id=db_machine.id,
        statusChanges=status_changes,
        currentStatus=db_machine.current_status
    )
    return machine

@app.delete("/api/machines/{machine_id}", status_code=204)
async def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    db_machine = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
    if db_machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(db_machine)
    db.commit()
    return {"message": "Machine deleted"}

@app.post("/api/generate_machines")
async def generate_machines(db: Session = Depends(get_db)):
    for i in range(100):
        machine_id = f'{i+1:04d}'
        status_changes = generate_status_changes()
        
        # Create machine
        db_machine = MachineDB(id=machine_id, current_status=status_changes[-1].status if status_changes else None)
        db.add(db_machine)
        
        # Create status changes
        for sc in status_changes:
            db_status_change = StatusChangeDB(
                machine_id=machine_id,
                status=sc.status,
                start_time=datetime.fromisoformat(sc.startTime)
            )
            db.add(db_status_change)
    
    db.commit()
    return {"message": "Machines generated and stored in the database"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)