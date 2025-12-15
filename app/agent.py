# app/agent.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import re # Import the regular expression library
from .tools import HRIS_Tool, Email_Tool

# ... (dotenv and genai configuration) ...
load_dotenv()

# --- THIS IS THE CRITICAL PART ---
# Configure the Gemini client and check for the key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

# ... (dotenv and genai configuration) ...

class LeaveManagementAgent:
    def __init__(self, hris_tool: HRIS_Tool, email_tool: Email_Tool):
        self.hris_tool = hris_tool
        self.email_tool = email_tool
        self.model = genai.GenerativeModel('models/gemini-2.5-pro')

    def run_agentic_workflow(self, user_query: str):
        print(f"🤖 Agent activated with goal: '{user_query}'")

        available_tools = [
            "get_leave_balance(employee_id)",
            "submit_leave_application(employee_id, days_requested)",
            "send_email(recipient_email, subject, body)"
        ]

        # Start the conversation history with a clear system prompt
        prompt = (
            f"You are an HR assistant. Your goal is to completely fulfill the user's request. "
            f"User's request: '{user_query}'.\n"
            f"Available tools: {available_tools}.\n"
            f"Follow these steps: 1. Check balance. 2. If sufficient, submit application. 3. Finish by composing and sending a confirmation email.\n"
            f"What is the first tool call you should make? Only respond with the function call."
        )

        # Start the Think -> Act -> Observe loop
        for i in range(5): # Loop up to 5 times
            print(f"\n--- Loop {i+1}: Sending Prompt to Gemini ---")
            print(prompt)
            print("------------------------------------------\n")
            
            # 1. THINK
            response = self.model.generate_content(prompt)
            action_string = response.text.strip().replace("`", "") # Clean up markdown backticks
            print(f"🤖 Gemini's Response (Next Action): {action_string}")

            # 2. ACT
            if "get_leave_balance" in action_string:
                employee_id = re.search(r"employee_id='(.*?)'", action_string).group(1)
                tool_result = self.hris_tool.get_leave_balance(employee_id)
                print(f"⚙️ Executed Tool: get_leave_balance. Result: {tool_result}")

            elif "submit_leave_application" in action_string:
                employee_id = re.search(r"employee_id='(.*?)'", action_string).group(1)
                days = int(re.search(r"days_requested=(\d+)", action_string).group(1))
                tool_result = self.hris_tool.submit_leave_application(employee_id, days)
                print(f"⚙️ Executed Tool: submit_leave_application. Result: {tool_result}")

            elif "send_email" in action_string:
                subject = re.search(r"subject='(.*?)'", action_string).group(1)
                body = re.search(r"body='(.*?)'", action_string).group(1)
                employee_id = "priya_k" # In a real app, you'd track this
                employee_data = self.hris_tool.get_employee_data(employee_id)
                tool_result = self.email_tool.send_email(employee_data.email, subject, body)
                print(f"⚙️ Executed Tool: send_email. Result: {tool_result}")
                
                return {"status": "complete", "final_step": tool_result}
            
            else:
                print("⚠️ Agent decided no further action was needed or action was unclear.")
                return {"status": "incomplete", "reason": "Agent halted."}

            # 3. OBSERVE: This is the corrected prompt logic
            # We append the function call it made and the observation (result)
            # Then we ask it for the next step.
            prompt = (
                f"{prompt}\n"
                f"Function Call: {action_string}\n"
                f"Observation: {tool_result}\n"
                f"What is the next tool call you should make to continue the process?"
            )

        return {"status": "incomplete", "reason": "Agent reached step limit."}