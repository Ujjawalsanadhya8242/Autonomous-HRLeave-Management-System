# app/schemas.py
from pydantic import BaseModel, Field

class LeaveRequest(BaseModel):
    employee_id: str = Field(..., description="The unique identifier for the employee.")
    days_requested: int = Field(..., gt=0, description="The number of leave days requested.")

class EmployeeData(BaseModel):
    name: str
    email: str
    leave_balance: int
    total_leaves: int = 18
    manager_id: str  # <-- ADD THIS LINE

# Add this new model for the agentic workflow
class AgentQuery(BaseModel):
    query: str    