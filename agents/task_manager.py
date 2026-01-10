"""
Task Manager Orchestrator
Coordinates between different agent implementations
"""
from typing import Optional
from agents.crewai_agent import CrewAITaskAgent
from agents.google_adk_agent import GoogleADKAgent
from observability.langfuse_config import trace_agent_execution, log_agent_event
import os

class TaskManager:
    """Main task manager that orchestrates different agents"""
    
    def __init__(self, agent_type: str = "google_adk"):
        """
        Initialize the task manager
        
        Args:
            agent_type: Type of agent to use ("crewai" or "google_adk")
        """
        self.agent_type = agent_type
        self.agent = None
        
        if agent_type == "crewai":
            try:
                self.agent = CrewAITaskAgent()
                log_agent_event("task_manager_initialized", "task_manager", {"agent_type": "crewai"})
            except Exception as e:
                log_agent_event("task_manager_init_failed", "task_manager", {"agent_type": "crewai", "error": str(e)})
                raise
        elif agent_type == "google_adk":
            try:
                self.agent = GoogleADKAgent()
                log_agent_event("task_manager_initialized", "task_manager", {"agent_type": "google_adk"})
            except Exception as e:
                log_agent_event("task_manager_init_failed", "task_manager", {"agent_type": "google_adk", "error": str(e)})
                raise
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def process(self, user_request: str) -> str:
        """
        Process a user request using the configured agent
        
        Args:
            user_request: User's task management request
            
        Returns:
            Response from the agent
        """
        trace = trace_agent_execution(
            agent_name=f"task_manager_{self.agent_type}",
            task=user_request,
            metadata={"agent_type": self.agent_type}
        )
        
        try:
            if self.agent_type == "crewai":
                result = self.agent.process_task(user_request)
            else:
                result = self.agent.process_request(user_request)
            
            log_agent_event(
                "task_processed",
                "task_manager",
                {"agent_type": self.agent_type, "request": user_request, "success": True}
            )
            
            return result
        
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            log_agent_event(
                "task_processing_error",
                "task_manager",
                {"agent_type": self.agent_type, "error": str(e)}
            )
            return error_msg

