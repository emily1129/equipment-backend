from pydantic import BaseModel
from typing import List

class StatusChange(BaseModel):
    status: str
    startTime: str

class Machine(BaseModel):
    id: str
    statusChanges: List[StatusChange]
    currentStatus: str