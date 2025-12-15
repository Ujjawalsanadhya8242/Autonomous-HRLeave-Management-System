Autonomous HR Leave Management System

A production-style backend system that manages employee leave requests using a combination of agentic AI workflows and a stateful approval lifecycle. Built with FastAPI, Gemini (LLM), and clean backend architecture principles.

This is not a CRUD demo. The goal of this project is to demonstrate how AI agents can orchestrate real business workflows end-to-end.

What This Project Does

An employee can:

Request leave

Automatically trigger manager approval

Receive email notifications

Track request status

The system:

Validates leave balance

Creates and tracks request state

Sends approval/denial emails

Deducts leave only after approval

Core Concepts Demonstrated
1. Agentic AI Workflow (Think → Act → Observe)

The LeaveManagementAgent uses an LLM (Gemini) to:

Reason about the user's intent

Decide which tool to call next

Observe tool output

Continue until the task is complete

This mirrors real autonomous agent behavior, not prompt-response chat.

2. Stateful Leave Lifecycle

Leave requests move through defined states:

PENDING_APPROVAL → APPROVED → (Leave Deducted)
                 → DENIED

State is stored in an in-memory database (RequestStateDB), simulating how real HR systems track workflow progress.

3. Manager Approval via Email Actions

Managers receive real emails containing approval and denial links.

Clicking a link:

Updates request state

Triggers final agentic actions

Notifies the employee automatically

Tech Stack

FastAPI – Backend API

Python 3.10+

Gemini LLM – Agent reasoning

SMTP (Gmail) – Email notifications

Pydantic – Data validation

In-memory databases – Mock HRIS + request tracking

Project Structure
app/
├── agent.py        # Agentic AI logic (Think → Act → Observe)
├── main.py         # FastAPI application & endpoints
├── tools.py        # HRIS and Email tools
├── database.py     # Mock HRIS + request state DB
├── schemas.py      # Pydantic models
🔌 API Endpoints
1️Request Leave
POST /request-leave

Creates a leave request and notifies the manager.

2️Handle Approval
GET /handle-approval?request_id=...&action=approve|deny

Triggered via manager email links.

3️Check Request Status
GET /request-status/{request_id}

Returns current request state.

Environment Variables

Create a .env file:

GOOGLE_API_KEY=your_gemini_api_key
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

Gmail requires App Passwords (not your actual password).

Running the Project
pip install -r requirements.txt
uvicorn app.main:app --reload

Visit:

http://127.0.0.1:8000/docs
Why This Project Matters

Most AI projects stop at prompt engineering.

This project shows:

How AI agents drive backend logic

How workflows persist beyond a single request

How to combine LLM reasoning with deterministic systems

This is the kind of architecture used in real internal tools, not tutorials.

Limitations (Intentional)

In-memory DBs (easy to replace with PostgreSQL)

No auth layer

Single-service design

These were skipped to focus on agentic workflow design.

Future Improvements

Persistent database

Role-based authentication

Background task queues (Celery / Redis)

UI dashboard

Multi-agent coordination

Author

Ujjawal Sanadhya
