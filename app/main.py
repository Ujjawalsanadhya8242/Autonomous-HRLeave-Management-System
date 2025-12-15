# # app/main.py

# from fastapi import FastAPI, HTTPException
# # 👇 IMPORT THE NEW SCHEMA
# from .schemas import AgentQuery
# from .tools import HRIS_Tool, Email_Tool
# from .agent import LeaveManagementAgent

# app = FastAPI(
#     title="Autonomous HR Leave Assistant API",
#     description="Manages leave applications using an agentic AI approach.",
#     version="3.0.0" # Version up!
# )

# # --- Dependency Injection: Initialize tools and agent ---
# hris = HRIS_Tool()
# mailer = Email_Tool()
# agent = LeaveManagementAgent(hris_tool=hris, email_tool=mailer)


# # --- 👇 THIS IS THE UPDATED ENDPOINT ---
# @app.post("/apply-for-leave", summary="Submit a leave application using the agent")
# def apply_for_leave(request: AgentQuery):
#     try:
#         # Call the NEW agentic workflow method
#         result = agent.run_agentic_workflow(user_query=request.query)
#         return {"status": "workflow_completed", "final_result": result}
#     except Exception as e:
#         # Catch any exceptions during the agent's run
#         raise HTTPException(status_code=500, detail=f"An error occurred in the agent workflow: {str(e)}")


# @app.get("/")
# def read_root():
#     return {"message": "HR Leave Assistant is running."}



from fastapi import FastAPI, HTTPException, Query
from .tools import Email_Tool
from .database import hris_db, request_db

# --- App and Tool Initialization ---
app = FastAPI(
    title="Autonomous HR Leave Assistant (Stateful)",
    description="Manages multi-step leave applications using a stateful workflow.",
    version="4.0.0"
)

email_tool = Email_Tool()

# --- Stateful API Endpoints ---

@app.post("/request-leave", summary="Step 1: Employee submits a leave request")
async def request_leave(employee_id: str, days_requested: int, reason: str):
    """
    Initiates a leave request. This creates a record, sets its status to
    'PENDING_APPROVAL', and notifies the manager.
    """
    employee = hris_db.get_employee_data(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found.")
    
    if employee.leave_balance < days_requested:
        raise HTTPException(status_code=400, detail="Insufficient leave balance.")

    manager = hris_db.get_employee_data(employee.manager_id)
    if not manager:
        raise HTTPException(status_code=500, detail="Manager not found for this employee.")
    
    # Create the request in our state database
    request_id = request_db.create_request(
        employee_id=employee_id,
        manager_id=employee.manager_id,
        days=days_requested,
        reason=reason
    )

    # --- Agentic Action: Notify Manager for Approval ---
    approval_link = f"http://127.0.0.1:8000/handle-approval?request_id={request_id}&action=approve"
    denial_link = f"http://127.0.0.1:8000/handle-approval?request_id={request_id}&action=deny"

    email_subject = f"Leave Request from {employee.name} (ID: {employee_id})"
    email_body = f"""
    Hello {manager.name},

    {employee.name} has requested {days_requested} day(s) of leave.
    Reason: {reason}

    Please review and take action using the links below:

    ✅ Approve: {approval_link}
    ❌ Deny: {denial_link}

    Request ID: {request_id}
    """
    email_tool.send_email(recipient_email=manager.email, subject=email_subject, body=email_body)
    
    return {
        "message": "Request successfully submitted. Awaiting manager approval.",
        "request_id": request_id,
        "status": "PENDING_APPROVAL"
    }


@app.get("/handle-approval", summary="Step 2: Manager approves or denies the request")
async def handle_approval(request_id: str, action: str = Query(..., enum=["approve", "deny"])):
    """
    This endpoint is triggered when a manager clicks an approval/denial link.
    It updates the request state and performs the final actions.
    """
    leave_request = request_db.get_request(request_id)
    if not leave_request or leave_request["status"] != "PENDING_APPROVAL":
        raise HTTPException(status_code=404, detail="Request not found or has already been processed.")

    employee = hris_db.get_employee_data(leave_request["employee_id"])
    if not employee:
        raise HTTPException(status_code=500, detail="Original employee data not found.")

    if action == "approve":
        # Update state to APPROVED
        request_db.update_status(request_id, "APPROVED")
        
        # --- Final Agentic Action: Deduct Leave and Notify Employee ---
        # Corrected line
        hris_db.deduct_leave(leave_request["employee_id"], leave_request["days_requested"])
        email_tool.send_email(
            recipient_email=employee.email,
            subject="Leave Request Approved",
            body=f"Hi {employee.name},\n\nYour leave request ({leave_request['reason']}) has been approved."
        )
        return {"message": f"Request {request_id} has been APPROVED."}
    
    if action == "deny":
        # Update state to DENIED
        request_db.update_status(request_id, "DENIED")

        # --- Final Agentic Action: Notify Employee of Denial ---
        email_tool.send_email(
            recipient_email=employee.email,
            subject="Leave Request Denied",
            body=f"Hi {employee.name},\n\nUnfortunately, your leave request ({leave_request['reason']}) has been denied."
        )
        return {"message": f"Request {request_id} has been DENIED."}


@app.get("/request-status/{request_id}", summary="Step 3: Check the status of a request")
async def get_request_status(request_id: str):
    """Allows anyone to check the status of a request using its ID."""
    leave_request = request_db.get_request(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return leave_request