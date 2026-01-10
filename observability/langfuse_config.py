"""
Langfuse Observability Configuration
Sets up Langfuse for tracking agent usage, traces, and metrics
"""
import os
import warnings
from langfuse import Langfuse
from dotenv import load_dotenv

# Suppress Langfuse context warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langfuse")

load_dotenv()

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

def get_langfuse_client():
    """Get the Langfuse client instance"""
    return langfuse

def create_trace(name: str, metadata: dict = None):
    """
    Create a trace using Langfuse
    
    Args:
        name: Name of the trace
        metadata: Metadata dictionary
        
    Returns:
        A span object that represents the trace (or None if fails)
    """
    try:
        # Try using start_as_current_span as context manager
        span = langfuse.start_as_current_span(
            name=name,
            metadata=metadata or {}
        )
        return span
    except Exception as e:
        # If that fails, try alternative methods
        try:
            # Try creating an event instead
            langfuse.create_event(
                name=name,
                metadata=metadata or {}
            )
            return None  # Events don't return span objects
        except Exception:
            # Silently fail - observability is optional
            return None

def end_span(output: str = None):
    """End the current span with optional output"""
    try:
        if output:
            langfuse.update_current_span(output=output)
    except Exception:
        # Silently ignore - span context may not be active
        pass

def trace_agent_execution(agent_name: str, task: str, result: str = None, metadata: dict = None):
    """
    Create a trace for agent execution
    
    Args:
        agent_name: Name of the agent (e.g., "crewai_task_manager", "google_adk_agent")
        task: Description of the task being performed
        result: Result of the task execution
        metadata: Additional metadata about the execution
    """
    try:
        # Use start_span which automatically creates a trace
        span = langfuse.start_span(
            name=f"{agent_name}_execution",
            metadata={
                "agent": agent_name,
                "task": task,
                **(metadata or {})
            }
        )
        
        if result:
            langfuse.update_current_span(output=result)
        
        langfuse.update_current_span(name=task)
        return span
    except Exception as e:
        # Return None if trace creation fails
        return None

def log_agent_event(event_name: str, agent_name: str, data: dict):
    """
    Log a custom event for agent observability
    
    Args:
        event_name: Name of the event
        agent_name: Name of the agent
        data: Event data
    """
    try:
        # Use create_event method
        langfuse.create_event(
            name=event_name,
            metadata={
                "agent": agent_name,
                **data
            }
        )
    except Exception as e:
        # Silently fail to not break the application
        # Events are not critical for core functionality
        pass

def create_span(name: str, metadata: dict = None):
    """Create a span"""
    try:
        return langfuse.start_span(name=name, metadata=metadata or {})
    except Exception:
        return None

