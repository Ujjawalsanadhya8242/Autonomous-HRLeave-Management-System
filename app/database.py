import uuid
from typing import Dict, TypedDict
from dataclasses import dataclass
from .schemas import EmployeeData # Assuming schemas.py is in the same 'app' directory

# --- Data Structures ---
# You can keep EmployeeData in schemas.py or move it here. Let's assume it's in schemas.py.
# from .schemas import EmployeeData

class LeaveRequest(TypedDict):
    """Represents a single leave request being tracked."""
    request_id: str
    employee_id: str
    manager_id: str
    status: str  # e.g., "PENDING_APPROVAL", "APPROVED", "DENIED"
    days_requested: int
    reason: str

# --- Mock Databases ---
class HRISDatabase:
    """A mock HR Information System database."""
    def __init__(self):
        # Using unique IDs and adding manager_id for the approval workflow
        self._employee_data: Dict[str, EmployeeData] = {
            "E101": EmployeeData(name="Priya K.", email="ujjawalsanadhya5@gmail.com", leave_balance=8, manager_id="M501", total_leaves=20),
            "E102": EmployeeData(name="Rohan M.", email="rohan.m@example.com", manager_id="M501", leave_balance=3, total_leaves=20),
            "M501": EmployeeData(name="Vikram Singh", email="ujjawalsanadhya5@gmail.com", manager_id="", leave_balance=30, total_leaves=30),
        }

    def get_employee_data(self, employee_id: str) -> EmployeeData | None:
        """Retrieves the full data object for a single employee."""
        return self._employee_data.get(employee_id)

    def deduct_leave(self, employee_id: str, days: int) -> bool:
        """Deducts leave from an employee's balance."""
        employee = self.get_employee_data(employee_id)
        if employee and employee.leave_balance >= days:
            employee.leave_balance -= days
            return True
        return False

class RequestStateDB:
    """A mock in-memory DB to track the state of leave requests."""
    def __init__(self):
        self._requests: Dict[str, LeaveRequest] = {}

    def create_request(self, employee_id: str, manager_id: str, days: int, reason: str) -> str:
        request_id = str(uuid.uuid4())
        self._requests[request_id] = LeaveRequest(
            request_id=request_id,
            employee_id=employee_id,
            manager_id=manager_id,
            status="PENDING_APPROVAL",
            days_requested=days,
            reason=reason
        )
        print(f"✅ New Request Created: {self._requests[request_id]}")
        return request_id

    def get_request(self, request_id: str) -> LeaveRequest | None:
        return self._requests.get(request_id)

    def update_status(self, request_id: str, status: str) -> bool:
        if request_id in self._requests:
            self._requests[request_id]["status"] = status
            print(f"🔄 Request Updated: {self._requests[request_id]}")
            return True
        return False

# --- Create Singleton Instances ---
# These will be imported and used by your main app
hris_db = HRISDatabase()
request_db = RequestStateDB()