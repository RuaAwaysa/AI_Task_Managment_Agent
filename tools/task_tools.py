"""
Task Management Tools
These tools are used by AI agents to manage tasks
"""
from typing import List, Dict, Optional
import json
from datetime import datetime
from observability.langfuse_config import log_agent_event

# In-memory task storage (in production, use a database)
tasks_db: List[Dict] = []

class TaskTools:
    """Tools for task management operations"""
    
    @staticmethod
    def create_task(title: str, description: str = "", priority: str = "medium", due_date: str = None) -> Dict:
        """
        Create a new task
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high)
            due_date: Due date in ISO format (YYYY-MM-DD)
        """
        task = {
            "id": len(tasks_db) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        tasks_db.append(task)
        
        log_agent_event(
            "task_created",
            "task_manager",
            {"task_id": task["id"], "title": title, "priority": priority}
        )
        
        return task
    
    @staticmethod
    def list_tasks(status: Optional[str] = None) -> List[Dict]:
        """
        List all tasks, optionally filtered by status
        
        Args:
            status: Filter by status (pending, in_progress, completed)
        """
        if status:
            filtered_tasks = [t for t in tasks_db if t["status"] == status]
            log_agent_event("tasks_listed", "task_manager", {"status": status, "count": len(filtered_tasks)})
            return filtered_tasks
        else:
            log_agent_event("tasks_listed", "task_manager", {"count": len(tasks_db)})
            return tasks_db
    
    @staticmethod
    def get_task(task_id: int) -> Optional[Dict]:
        """
        Get a specific task by ID
        
        Args:
            task_id: Task ID
        """
        task = next((t for t in tasks_db if t["id"] == task_id), None)
        if task:
            log_agent_event("task_retrieved", "task_manager", {"task_id": task_id})
        return task
    
    @staticmethod
    def update_task(task_id: int, title: str = None, description: str = None, 
                   priority: str = None, status: str = None, due_date: str = None) -> Optional[Dict]:
        """
        Update an existing task
        
        Args:
            task_id: Task ID
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)
            due_date: New due date (optional)
        """
        task = next((t for t in tasks_db if t["id"] == task_id), None)
        if not task:
            return None
        
        if title:
            task["title"] = title
        if description:
            task["description"] = description
        if priority:
            task["priority"] = priority
        if status:
            task["status"] = status
            if status == "completed":
                task["completed_at"] = datetime.now().isoformat()
        if due_date:
            task["due_date"] = due_date
        
        log_agent_event(
            "task_updated",
            "task_manager",
            {"task_id": task_id, "updates": {"status": status, "priority": priority}}
        )
        
        return task
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
        """
        global tasks_db
        initial_count = len(tasks_db)
        tasks_db = [t for t in tasks_db if t["id"] != task_id]
        
        if len(tasks_db) < initial_count:
            log_agent_event("task_deleted", "task_manager", {"task_id": task_id})
            return True
        return False
    
    @staticmethod
    def get_tasks_by_priority(priority: str) -> List[Dict]:
        """
        Get tasks filtered by priority
        
        Args:
            priority: Priority level (low, medium, high)
        """
        filtered = [t for t in tasks_db if t["priority"] == priority]
        log_agent_event("tasks_filtered", "task_manager", {"priority": priority, "count": len(filtered)})
        return filtered
    
    @staticmethod
    def get_statistics() -> Dict:
        """Get task statistics"""
        stats = {
            "total": len(tasks_db),
            "pending": len([t for t in tasks_db if t["status"] == "pending"]),
            "in_progress": len([t for t in tasks_db if t["status"] == "in_progress"]),
            "completed": len([t for t in tasks_db if t["status"] == "completed"]),
            "high_priority": len([t for t in tasks_db if t["priority"] == "high"]),
            "medium_priority": len([t for t in tasks_db if t["priority"] == "medium"]),
            "low_priority": len([t for t in tasks_db if t["priority"] == "low"]),
        }
        log_agent_event("statistics_retrieved", "task_manager", stats)
        return stats

