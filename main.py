# main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from schemas import Machine
from data_generator import generate_machines
import crud

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
    return crud.get_machines(db)

@app.get("/api/machines/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str, db: Session = Depends(get_db)):
    machine = crud.get_machine(db, machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@app.delete("/api/machines/{machine_id}", status_code=204)
async def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    if not crud.delete_machine(db, machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"message": "Machine deleted"}

@app.post("/api/generate_machines")
async def generate_initial_data(db: Session = Depends(get_db)):
    return generate_machines(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)