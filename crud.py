# crud.py

from sqlalchemy.orm import Session
from typing import List
from models import MachineDB, StatusChangeDB
from schemas import Machine, StatusChange

def get_machines(db: Session) -> List[Machine]:
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

def get_machine(db: Session, machine_id: str) -> Machine:
    db_machine = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
    if db_machine is None:
        return None
    
    db_status_changes = db.query(StatusChangeDB).filter(StatusChangeDB.machine_id == machine_id).order_by(StatusChangeDB.start_time).all()
    status_changes = [StatusChange(status=sc.status, startTime=sc.start_time.isoformat()) for sc in db_status_changes]
    return Machine(
        id=db_machine.id,
        statusChanges=status_changes,
        currentStatus=db_machine.current_status
    )

def delete_machine(db: Session, machine_id: str) -> bool:
    db_machine = db.query(MachineDB).filter(MachineDB.id == machine_id).first()
    if db_machine is None:
        return False
    db.delete(db_machine)
    db.commit()
    return True