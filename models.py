from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base

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