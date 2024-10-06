from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from models import MachineDB, StatusChangeDB
from schemas import StatusChange, Machine
import logging

def get_random_time(start: datetime, end: datetime) -> str:
    random_time = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    return random_time.strftime("%Y-%m-%d %H:%M:%S")

def generate_status_changes() -> tuple[list[StatusChange], str]:
    statuses = ['生產', '閒置', '當機', '裝機', '工程借機', '其他']
    changes = []
    now = datetime.now().replace(microsecond=0)
    start_of_day = now.replace(hour=0, minute=0, second=0)

    number_of_changes = random.randint(1, 7)

    for _ in range(number_of_changes):
        status = random.choice(statuses)
        start_time = get_random_time(start_of_day, now)
        changes.append(StatusChange(status=status, startTime=start_time))

    changes.sort(key=lambda x: x.startTime)

    if changes:
        changes[0].startTime = start_of_day.strftime("%Y-%m-%d %H:%M:%S")
        current_status = changes[-1].status
    else:
        current_status = random.choice(statuses)
        changes.append(StatusChange(status=current_status, startTime=start_of_day.strftime("%Y-%m-%d %H:%M:%S")))

    return changes, current_status
    
def generate_machines(db: Session, count: int = 100) -> list[Machine]:
    generated_machines = []

    for i in range(count):
        machine_id = f'{i+1:04d}'
        status_changes, _ = generate_status_changes() 
        
        # ensure the current status is the last one in the list
        current_status = status_changes[-1].status if status_changes else None
        
        # create machine
        db_machine = MachineDB(id=machine_id, current_status=current_status)
        db.add(db_machine)
        
        # create status changes
        for sc in status_changes:
            db_status_change = StatusChangeDB(
                machine_id=machine_id,
                status=sc.status,
                start_time=datetime.strptime(sc.startTime, "%Y-%m-%d %H:%M:%S")
            )
            db.add(db_status_change)
        
        # append to list of generated machines
        generated_machines.append(Machine(
            id=machine_id,
            statusChanges=status_changes,
            currentStatus=current_status
        ))
    
    db.commit()
    generated_machines.sort(key=lambda x: x.id)
    return generated_machines

def update_machines(db: Session, count: int = 100) -> list[Machine]:
    updated_machines = []
    now = datetime.now().replace(microsecond=0)

    existing_machines = db.query(MachineDB).all()

    for machine in existing_machines:
        new_status = random.choice(['生產', '閒置', '當機', '裝機', '工程借機', '其他'])
        
        # create a new status change record
        new_status_change = StatusChangeDB(
            machine_id=machine.id,
            status=new_status,
            start_time=now
        )
        db.add(new_status_change)
        
        # get all status changes for a machine, including the new one
        status_changes = db.query(StatusChangeDB).filter(StatusChangeDB.machine_id == machine.id).order_by(StatusChangeDB.start_time.desc()).all()
        
        # most recent status is now the first in the list (descending order
        most_recent_status = status_changes[0].status if status_changes else new_status
        
        logging.info(f"Machine {machine.id}: Most recent status is {most_recent_status} at {status_changes[0].start_time}")
        
        # update the machine's current status to the most recent status change
        machine.current_status = most_recent_status

        # create Machine object for return
        updated_machine = Machine(
            id=machine.id,
            statusChanges=[StatusChange(status=sc.status, startTime=sc.start_time.isoformat()) for sc in reversed(status_changes)],
            currentStatus=most_recent_status
        )
        updated_machines.append(updated_machine)

    if len(existing_machines) < count:
        new_machines = generate_machines(db, count - len(existing_machines))
        updated_machines.extend(new_machines)

    db.commit()

    # sort the updated_machines list by machine ID
    updated_machines.sort(key=lambda m: m.id)

    return updated_machines