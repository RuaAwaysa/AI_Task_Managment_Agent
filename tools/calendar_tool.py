"""
Google Calendar Integration Tool
This tool allows AI agents to interact with Google Calendar
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from observability.langfuse_config import log_agent_event

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarTool:
    """Tools for Google Calendar operations"""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Initialize Calendar Tool
        
        Args:
            credentials_path: Path to Google OAuth2 credentials JSON file
        """
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = 'token.pickle'
        
        # Load existing token if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    log_agent_event(
                        "calendar_auth_failed",
                        "calendar_tool",
                        {"error": "credentials.json not found"}
                    )
                    return
            
            # Save credentials for next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build the service
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            log_agent_event("calendar_authenticated", "calendar_tool", {"status": "success"})
        except Exception as e:
            log_agent_event("calendar_auth_failed", "calendar_tool", {"error": str(e)})
    
    def create_event(self, summary: str, description: str = "", 
                    start_time: str = None, end_time: str = None,
                    location: str = "") -> Optional[Dict]:
        """
        Create a calendar event
        
        Args:
            summary: Event title
            description: Event description
            start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
            end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS)
            location: Event location
        """
        if not self.service:
            return None
        
        # Default to 1 hour from now if times not provided
        if not start_time:
            start = datetime.now() + timedelta(hours=1)
            start_time = start.isoformat()
        if not end_time:
            end = datetime.fromisoformat(start_time.replace('Z', '+00:00')) + timedelta(hours=1)
            end_time = end.isoformat()
        
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        try:
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            log_agent_event(
                "calendar_event_created",
                "calendar_tool",
                {"event_id": event_result.get('id'), "summary": summary}
            )
            return event_result
        except Exception as e:
            log_agent_event("calendar_event_creation_failed", "calendar_tool", {"error": str(e)})
            return None
    
    def list_events(self, max_results: int = 10, time_min: str = None) -> List[Dict]:
        """
        List upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
            time_min: Lower bound for event time (ISO format)
        """
        if not self.service:
            return []
        
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            log_agent_event("calendar_events_listed", "calendar_tool", {"count": len(events)})
            return events
        except Exception as e:
            log_agent_event("calendar_events_list_failed", "calendar_tool", {"error": str(e)})
            return []
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """
        Get a specific calendar event
        
        Args:
            event_id: Google Calendar event ID
        """
        if not self.service:
            return None
        
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            log_agent_event("calendar_event_retrieved", "calendar_tool", {"event_id": event_id})
            return event
        except Exception as e:
            log_agent_event("calendar_event_retrieval_failed", "calendar_tool", {"error": str(e)})
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: Google Calendar event ID
        """
        if not self.service:
            return False
        
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            log_agent_event("calendar_event_deleted", "calendar_tool", {"event_id": event_id})
            return True
        except Exception as e:
            log_agent_event("calendar_event_deletion_failed", "calendar_tool", {"error": str(e)})
            return False
    
    def create_event_from_task(self, task: Dict) -> Optional[Dict]:
        """
        Create a calendar event from a task
        
        Args:
            task: Task dictionary with title, description, due_date
        """
        if not task.get('due_date'):
            return None
        
        return self.create_event(
            summary=f"Task: {task['title']}",
            description=task.get('description', ''),
            start_time=task['due_date'],
            location=""
        )

