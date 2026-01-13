"""
Google ADK (Agent Development Kit) Agent Implementation
This agent uses Google's Gemini API for task management
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools.task_tools import TaskTools
from tools.calendar_tool import CalendarTool
from observability.langfuse_config import trace_agent_execution, log_agent_event, get_langfuse_client
from typing import Dict, Any
import json
import re
from datetime import datetime, timedelta

load_dotenv()

class GoogleADKAgent:
    """Google ADK-based task management agent using Gemini"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the Google ADK agent
        
        Args:
            model_name: Name of the Gemini model to use (default: gemini-2.5-flash)
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set in .env file")
        
        genai.configure(api_key=api_key)
        
        # Try to use the model name, or fallback to available models
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception:
            try:
                if not model_name.startswith("models/"):
                    self.model = genai.GenerativeModel(f"models/{model_name}")
                else:
                    self.model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception:
                self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        self.task_tools = TaskTools()
        self.calendar_tool = CalendarTool() if os.path.exists("credentials.json") else None
        
        log_agent_event("agent_initialized", "google_adk_agent", {"model": model_name, "status": "success"})
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent"""
        return """You are a helpful task management assistant powered by Google's Gemini AI.
You can help users with the following operations:
1. Create tasks with title, description, priority (low/medium/high), and optional due date
2. List tasks, optionally filtered by status (pending/in_progress/completed)
3. Update task status or priority
4. Get task statistics
5. Create calendar events from tasks (if calendar integration is available)

When users make requests, analyze their intent and use the appropriate functions.
Always provide clear, helpful responses."""

    def _parse_user_request(self, user_request: str) -> Dict[str, Any]:
        """
        Parse user request and determine the action
        
        Args:
            user_request: User's request text
            
        Returns:
            Dictionary with action type and parameters
        """
        request_lower = user_request.lower()
        
        if "duplicate" in request_lower and any(word in request_lower for word in ['remove', 'delete', 'clean', 'check', 'find']):
            return {"action": "deduplicate", "request": user_request}
        
        if any(word in request_lower for word in ['create', 'add', 'new task']):
            return {"action": "create", "request": user_request}
        elif any(word in request_lower for word in ['list', 'show', 'get tasks', 'tasks']):
            return {"action": "list", "request": user_request}
        elif any(word in request_lower for word in ['update', 'change', 'modify', 'mark']):
            return {"action": "update", "request": user_request}
        elif any(word in request_lower for word in ['delete', 'remove']):
            return {"action": "delete", "request": user_request}
        elif any(word in request_lower for word in ['statistics', 'stats', 'summary', 'overview']):
            return {"action": "statistics", "request": user_request}
        else:
            return {"action": "general", "request": user_request}

    def _extract_task_info(self, user_request: str) -> Dict[str, Any]:
        """
        Extract task information from user request using Gemini
        Handles natural language dates (e.g., "tomorrow")
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
        Extract task details from this request into a JSON object.
        Current date: {current_date}
        
        Request: "{user_request}"
        
        Return JSON with keys:
        - title (string)
        - priority (low, medium, high) - only if explicitly mentioned
        - status (pending, in_progress, completed) - only if explicitly mentioned
        - due_date (YYYY-MM-DD) - convert relative dates like 'tomorrow', 'next friday' to this format.
        - task_id (integer) - if mentioned
        
        Respond ONLY with the JSON string.
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            return {}

    def _deduplicate_tasks(self) -> str:
        """Find and remove duplicate tasks using LLM"""
        tasks = self.task_tools.list_tasks()
        active_tasks = [t for t in tasks if t['status'] != 'canceled']
        
        if len(active_tasks) < 2:
            return "Not enough tasks to check for duplicates."
            
        task_list_data = [{k: v for k, v in t.items() if k in ['id', 'title', 'description']} for t in active_tasks]
        task_list_str = json.dumps(task_list_data, indent=2)
        
        prompt = f"""
        Analyze this list of tasks and identify duplicates based on semantic meaning.
        Example: "Finish course" and "Get course certificate" are duplicates.
        
        Tasks:
        {task_list_str}
        
        Return a JSON object where keys are the IDs of tasks to KEEP, and values are lists of IDs of duplicate tasks to REMOVE.
        Prefer keeping the task with the lower ID (older).
        If no duplicates, return {{}}.
        
        Response format (JSON only):
        {{
            "keep_id": [remove_id1, remove_id2]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            if "{" in text: text = text[text.find("{"):text.rfind("}")+1]
            duplicates_map = json.loads(text)
            
            removed_count = 0
            report = []
            for keep_id, remove_ids in duplicates_map.items():
                keep_task = self.task_tools.get_task(int(keep_id))
                for r_id in remove_ids:
                    r_task = self.task_tools.get_task(int(r_id))
                    if r_task and keep_task:
                        self.task_tools.delete_task(int(r_id))
                        report.append(f"Removed '{r_task['title']}' (duplicate of '{keep_task['title']}')")
                        removed_count += 1
            if removed_count > 0:
                log_agent_event("deduplication_performed", "google_adk_agent", {"removed_count": removed_count})
            return f"Removed {removed_count} duplicates:\n" + "\n".join(report) if removed_count else "No duplicates found."
        except Exception as e:
            return f"Error checking duplicates: {str(e)}"

    def _execute_action(self, action: str, params: Dict[str, Any]) -> str:
        """
        Execute the determined action
        
        Args:
            action: Action type (create, list, update, delete, statistics)
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        try:
            if action == "create":
                title = params.get("title", "Untitled Task")
                description = params.get("description", "")
                priority = params.get("priority", "medium")
                due_date = params.get("due_date")
                
                # Auto-set high priority if due date is near (within 24 hours)
                if due_date:
                    try:
                        due_dt = datetime.strptime(due_date, "%Y-%m-%d")
                        if 0 <= (due_dt - datetime.now()).days < 1:
                            priority = "high"
                    except ValueError:
                        pass
                
                task = self.task_tools.create_task(title, description, priority, due_date)
                return f"Task created successfully!\nID: {task['id']}\nTitle: {task['title']}\nPriority: {task['priority']}\nStatus: {task['status']}"
            
            elif action == "list":
                status = params.get("status")
                tasks = self.task_tools.list_tasks(status)
                
                if not tasks:
                    return "No tasks found."
                
                result = f"Found {len(tasks)} task(s):\n\n"
                for task in tasks:
                    result += f"• ID {task['id']}: {task['title']} ({task['status']}, {task['priority']} priority)\n"
                    if task.get('due_date'):
                        result += f"  Due: {task['due_date']}\n"
                    if task.get('description'):
                        result += f"  Description: {task['description']}\n"
                    result += "\n"
                
                return result
            
            elif action == "update":
                task_id = params.get("task_id")
                title = params.get("title")

                # Find task by ID or title
                task = None
                if task_id:
                    task = self.task_tools.get_task(task_id)
                elif title:
                    all_tasks = self.task_tools.list_tasks()
                    task = next((t for t in all_tasks if t["title"].lower() == title.lower()), None)

                if not task:
                    return "Task not found. Please check the ID or title."

                updated_task = self.task_tools.update_task(
                    task_id=task["id"],
                    status=params.get("status"),
                    priority=params.get("priority"),
                    title=params.get("title"),
                )

                return f"Task {updated_task['id']} updated successfully!\nTitle: {updated_task['title']}\nStatus: {updated_task['status']}\nPriority: {updated_task['priority']}"

            elif action == "delete":
                task_id = params.get("task_id")
                title = params.get("title")

                task = None
                if task_id:
                    task = self.task_tools.get_task(task_id)
                elif title:
                    all_tasks = self.task_tools.list_tasks()
                    task = next((t for t in all_tasks if t["title"].lower() == title.lower()), None)

                if not task:
                    return "Task not found. Please check the ID or title."

                self.task_tools.delete_task(task["id"])
                return f"Task {task['id']} deleted successfully!"

            elif action == "statistics":
                stats = self.task_tools.get_statistics()
                return f"""Task Statistics:
• Total Tasks: {stats['total']}
• Pending: {stats['pending']}
• In Progress: {stats['in_progress']}
• Completed: {stats['completed']}
• High Priority: {stats['high_priority']}
• Medium Priority: {stats['medium_priority']}
• Low Priority: {stats['low_priority']}"""

            elif action == "deduplicate":
                return self._deduplicate_tasks()

            else:
                return "I understand your request, but I'm not sure how to handle it. Try:\n- Creating a task\n- Listing tasks\n- Updating a task\n- Deleting a task\n- Getting statistics"

        except Exception as e:
            log_agent_event("action_execution_failed", "google_adk_agent", {"action": action, "error": str(e)})
            return f"Error executing action: {str(e)}"

    def process_request(self, user_request: str) -> str:
        """
        Process a user request using Google ADK
        
        Args:
            user_request: The user's task management request
            
        Returns:
            Response from the agent
        """
        from observability.langfuse_config import create_trace, end_span
        trace = create_trace(
            name="google_adk_task_processing",
            metadata={"user_request": user_request, "agent": "google_adk_agent"}
        )
        
        try:
            log_agent_event("task_processing_started", "google_adk_agent", {"request": user_request})
            
            # Parse the request
            parsed = self._parse_user_request(user_request)
            action = parsed["action"]
            
            # Extract parameters
            params = {}
            if action in ["create", "update", "delete"]:
                params = self._extract_task_info(user_request)
            
            # Execute the action
            result = self._execute_action(action, params)
            
            # Generate a friendly response (optional)
            response_prompt = f"""Based on the task management operation result below, provide a friendly, natural response to the user.

Operation Result:
{result}

User's Original Request:
{user_request}

Provide a concise, helpful response."""
            response = self.model.generate_content(response_prompt)
            final_result = response.text
            
            end_span(output=final_result)
            log_agent_event("task_processing_completed", "google_adk_agent", {"request": user_request, "success": True})
            
            return final_result
        
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            end_span(output=error_msg)
            log_agent_event("task_processing_failed", "google_adk_agent", {"error": str(e)})
            return error_msg
