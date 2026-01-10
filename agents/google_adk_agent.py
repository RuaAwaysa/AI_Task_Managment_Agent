"""
Google ADK (Agent Development Kit) Agent Implementation
This agent uses Google's Gemini API for task management
with optional integration to Notion and Serper.dev for search.
"""
import os
import json
import http.client
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any
from tools.task_tools import TaskTools
from tools.calendar_tool import CalendarTool
from observability.langfuse_config import log_agent_event, create_trace, end_span

load_dotenv()

class GoogleADKAgent:
    """Google ADK-based task management agent using Gemini"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.task_tools = TaskTools()
        self.calendar_tool = CalendarTool() if os.path.exists("credentials.json") else None

        log_agent_event("agent_initialized", "google_adk_agent", {"model": model_name, "status": "success"})

    # -----------------------------
    # Core Processing
    # -----------------------------
    def process_request(self, user_request: str) -> str:
        trace = create_trace("google_adk_task_processing", {"user_request": user_request})
        try:
            parsed = self._parse_user_request(user_request)
            action = parsed["action"]
            params = {}
            if action in ["create", "update", "delete"]:
                params = self._extract_task_info(user_request)
            
            result = self._execute_action(action, params)
            end_span(output=result)
            return result
        except Exception as e:
            end_span(output=str(e))
            return f"I encountered an error: {str(e)}"

    # -----------------------------
    # User request parsing
    # -----------------------------
    def _parse_user_request(self, user_request: str) -> Dict[str, Any]:
        request_lower = user_request.lower()
        if any(word in request_lower for word in ['create', 'add', 'new task']):
            return {"action": "create", "request": user_request}
        elif any(word in request_lower for word in ['list', 'show', 'get tasks', 'tasks']):
            return {"action": "list", "request": user_request}
        elif any(word in request_lower for word in ['update', 'change', 'modify', 'mark']):
            return {"action": "update", "request": user_request}
        elif any(word in request_lower for word in ['statistics', 'stats', 'summary', 'overview']):
            return {"action": "statistics", "request": user_request}
        elif any(word in request_lower for word in ['delete', 'remove']):
            return {"action": "delete", "request": user_request}
        else:
            return {"action": "general", "request": user_request}

    # -----------------------------
    # Task info extraction
    # -----------------------------
    def _extract_task_info(self, user_request: str) -> Dict[str, Any]:
        extraction_prompt = f"""Extract task information from: "{user_request}"
Return JSON: title, description, priority (low/medium/high), due_date (YYYY-MM-DD), task_id, status"""
        try:
            response = self.model.generate_content(extraction_prompt)
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            return json.loads(response_text)
        except Exception as e:
            log_agent_event("task_info_extraction_failed", "google_adk_agent", {"error": str(e)})
            return {}

    # -----------------------------
    # Action execution
    # -----------------------------
    def _execute_action(self, action: str, params: Dict[str, Any]) -> str:
        try:
            if action == "create":
                title = params.get("title", "Untitled Task")
                description = params.get("description", "")
                priority = params.get("priority", "medium")
                due_date = params.get("due_date")

                task = self.task_tools.create_task(title, description, priority, due_date)

                # Calendar event
                calendar_msg = ""
                if due_date and self.calendar_tool:
                    event_result = self.calendar_tool.create_event_from_task(task)
                    calendar_msg = " | Calendar event created" if event_result else " | Calendar event failed"

                # Notion integration
                notion_msg = self._send_task_to_notion(task)

                return f"Task created!\nID: {task['id']}\nTitle: {task['title']}\nPriority: {task['priority']}\nStatus: {task['status']}\n{calendar_msg}\n{notion_msg}"

            elif action == "list":
                tasks = self.task_tools.list_tasks(params.get("status"))
                if not tasks:
                    return "No tasks found."
                return "\n".join([f"{t['id']}: {t['title']} ({t['status']}, {t['priority']})" for t in tasks])

            elif action == "update":
                task_id = params.get("task_id")
                if not task_id:
                    return "Task ID required for update."
                task = self.task_tools.update_task(task_id, status=params.get("status"), priority=params.get("priority"), title=params.get("title"), description=params.get("description"))
                return f"Task {task_id} updated." if task else f"❌ Task {task_id} not found."

            elif action == "delete":
                task_id = params.get("task_id")
                if not task_id:
                    return "Task ID required for deletion."
                success = self.task_tools.delete_task(task_id)
                return f"Task {task_id} deleted." if success else f"❌ Task {task_id} not found."

            elif action == "statistics":
                stats = self.task_tools.get_statistics()
                return f"Tasks: {stats['total']}, Pending: {stats['pending']}, In Progress: {stats['in_progress']}, Completed: {stats['completed']}"

            else:
                return "I understand your request but cannot process it."

        except Exception as e:
            log_agent_event("action_execution_failed", "google_adk_agent", {"action": action, "error": str(e)})
            return f"Error executing action: {str(e)}"

    # -----------------------------
    # Serper search
    # -----------------------------
    def _serper_search(self, query: str) -> str:
        try:
            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({"q": query})
            headers = {
                'X-API-KEY': os.getenv("SERPER_API_KEY"),
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read()
            result = json.loads(data.decode("utf-8"))
            return result.get("organic", [{}])[0].get("snippet", "No result found")
        except Exception as e:
            log_agent_event("serper_search_failed", "google_adk_agent", {"error": str(e), "query": query})
            return "Error fetching search results"

    # -----------------------------
    # Notion Integration
    # -----------------------------
    def _send_task_to_notion(self, task: dict) -> str:
        database_id = os.getenv("NOTION_DATABASE_ID")
        secret = os.getenv("NOTION_INTERNAL_SECRET")
        if not database_id or not secret:
            return "Notion not configured."

        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": task.get("title", "Untitled Task")}}]},
                "Priority": {"select": {"name": task.get("priority", "Medium").capitalize()}},
                "Status": {"select": {"name": task.get("status", "Pending").capitalize()}},
            },
            "children": [
                {"object": "block", "type": "paragraph", "paragraph": {"text": [{"type": "text", "text": {"content": task.get("description", "")}}]}}
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                log_agent_event("task_sent_to_notion", "google_adk_agent", {"task_id": task.get("id")})
                return "Task sent to Notion successfully."
            else:
                return f"Failed to send task to Notion: {response.text}"
        except Exception as e:
            log_agent_event("task_notion_failed", "google_adk_agent", {"error": str(e)})
            return f"Error sending task to Notion: {str(e)}"