from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import Machine
import crud
from data_generator import generate_machines

router = APIRouter()

@router.get("/machines", response_model=List[Machine])
async def get_machines(db: Session = Depends(get_db)):
    return crud.get_machines(db)

@router.get("/machines/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str, db: Session = Depends(get_db)):
    machine = crud.get_machine(db, machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.delete("/machines/{machine_id}", status_code=204)
async def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    if not crud.delete_machine(db, machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"message": "Machine deleted"}

@router.post("/generate_machines")
async def generate_initial_data(db: Session = Depends(get_db)):
    return generate_machines(db)