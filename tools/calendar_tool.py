"""
Google Calendar Integration Tool
"""
import os
import pickle
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from observability.langfuse_config import log_agent_event

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarTool:
    """Optional Google Calendar integration"""

    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.service = None

        if os.path.exists(credentials_path):
            self._authenticate()
        else:
            log_agent_event(
                "calendar_disabled",
                "calendar_tool",
                {"reason": "credentials.json not found"},
            )

    def _authenticate(self):
        creds = None
        token_path = "token.pickle"

        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

        try:
            self.service = build("calendar", "v3", credentials=creds)
            log_agent_event(
                "calendar_authenticated",
                "calendar_tool",
                {"status": "success"},
            )
        except Exception as e:
            log_agent_event(
                "calendar_auth_failed",
                "calendar_tool",
                {"error": str(e)},
            )

    def create_event_from_task(self, task: Dict) -> Optional[Dict]:
        if not self.service or not task.get("due_date"):
            return None

        start = datetime.fromisoformat(task["due_date"])
        end = start + timedelta(hours=1)

        event = {
            "summary": f"Task: {task['title']}",
            "description": task.get("description", ""),
            "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        }

        try:
            created = (
                self.service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )

            log_agent_event(
                "calendar_event_created",
                "calendar_tool",
                {"event_id": created.get("id")},
            )

            return created

        except Exception as e:
            log_agent_event(
                "calendar_event_creation_failed",
                "calendar_tool",
                {"error": str(e)},
            )
            return None