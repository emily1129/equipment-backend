from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from models import MachineDB, StatusChangeDB
from schemas import StatusChange

def get_random_time(start: datetime, end: datetime) -> str:
    return (start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))).isoformat()

def generate_status_changes() -> list[StatusChange]:
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

def generate_machines(db: Session):
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