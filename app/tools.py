# app/tools.py
import smtplib
import os
from dotenv import load_dotenv
from typing import Dict
from .schemas import EmployeeData

from typing import Dict
from .schemas import EmployeeData

class HRIS_Tool:
    """A mock HR Information System database."""
    def __init__(self):
        self._employee_data: Dict[str, EmployeeData] = {
            "priya_k": EmployeeData(name="Priya K.", email="ujjawalsanadhya5@gmail.com", leave_balance=8),
            "rohan_m": EmployeeData(name="Rohan M.", email="rohan.m@example.com", leave_balance=3),
        }

    # --- METHOD 1: GET FULL EMPLOYEE DETAILS ---
    def get_employee_data(self, employee_id: str) -> EmployeeData | None:
        """Retrieves the full data object for a single employee."""
        return self._employee_data.get(employee_id)

    # --- METHOD 2: GET LEAVE BALANCE ---
    def get_leave_balance(self, employee_id: str) -> Dict:
        """Gets the current leave balance for a specific employee."""
        employee = self.get_employee_data(employee_id)
        if not employee:
            return {"error": "Employee not found"}
        return {"balance": employee.leave_balance, "total": employee.total_leaves}

    # --- METHOD 3: SUBMIT LEAVE APPLICATION ---
    def submit_leave_application(self, employee_id: str, days_requested: int) -> Dict:
        """Updates an employee's leave balance after a request."""
        employee = self.get_employee_data(employee_id)
        if not employee:
            return {"error": "Employee not found"}
        
        if employee.leave_balance < days_requested:
            return {"status": "failure", "reason": "Insufficient leave balance"}
        
        # Deduct the leave days
        employee.leave_balance -= days_requested
        return {"status": "success", "new_balance": employee.leave_balance}
    
    
# --- UPDATED Email_Tool ---
class Email_Tool:
    """A real Email Service that sends emails using Gmail."""
    def __init__(self):
        load_dotenv()  # Load variables from the .env file
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    # In app/tools.py

    def send_email(self, recipient_email: str, subject: str, body: str):
        if not self.sender_email or not self.sender_password:
            print("ERROR: Email credentials not set in .env file.")
            return {"status": "error", "reason": "Server not configured"}

        # Create the email message including the "From" header
        message = f"Subject: {subject}\n\nFrom: {self.sender_email}\nTo: {recipient_email}\n\n{body}"

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.sender_password)
                
                # THIS IS THE CORRECTED LINE:
                server.sendmail(self.sender_email, recipient_email, message.encode('utf-8'))
            
            print(f"Email successfully sent to {recipient_email}")
            return {"status": "email_sent"}
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {"status": "error", "reason": str(e)}