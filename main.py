from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import MachineDB, StatusChangeDB
from schemas import Machine, StatusChange
from data_generator import generate_machines

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def generate_initial_data(db: Session = Depends(get_db)):
    return generate_machines(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)