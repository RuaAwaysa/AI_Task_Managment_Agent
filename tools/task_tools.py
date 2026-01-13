"""
Task Management Tools
Used by AI agents to manage tasks (in-memory storage)
"""
from typing import List, Dict, Optional
from datetime import datetime
import itertools

from observability.langfuse_config import log_agent_event

# In-memory task storage
tasks_db: List[Dict] = []

# Safe incremental ID generator
_task_id_counter = itertools.count(start=1)


class TaskTools:
    """Tools for task management operations"""

    @staticmethod
    def create_task(
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> Dict:
        task = {
            "id": next(_task_id_counter),
            "title": title,
            "description": description,
            "priority": priority.lower(),
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }

        tasks_db.append(task)

        log_agent_event(
            "task_created",
            "task_tools",
            {
                "task_id": task["id"],
                "priority": task["priority"],
            },
        )

        return task

    @staticmethod
    def list_tasks(status: Optional[str] = None) -> List[Dict]:
        if status:
            result = [t for t in tasks_db if t["status"] == status]
        else:
            result = list(tasks_db)

        log_agent_event(
            "tasks_listed",
            "task_tools",
            {"status": status, "count": len(result)},
        )

        return result

    @staticmethod
    def get_task(task_id: int) -> Optional[Dict]:
        task = next((t for t in tasks_db if t["id"] == task_id), None)

        if task:
            log_agent_event(
                "task_retrieved",
                "task_tools",
                {"task_id": task_id},
            )

        return task

    @staticmethod
    def update_task(
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Optional[Dict]:

        task = TaskTools.get_task(task_id)
        if not task:
            return None

        if title:
            task["title"] = title
        if description:
            task["description"] = description
        if priority:
            task["priority"] = priority.lower()
        if due_date:
            task["due_date"] = due_date
        if status:
            task["status"] = status.lower()
            if status.lower() == "completed":
                task["completed_at"] = datetime.utcnow().isoformat()

        log_agent_event(
            "task_updated",
            "task_tools",
            {
                "task_id": task_id,
                "status": task.get("status"),
                "priority": task.get("priority"),
            },
        )

        return task

    @staticmethod
    def delete_task(task_id: int) -> bool:
        global tasks_db
        before = len(tasks_db)
        tasks_db = [t for t in tasks_db if t["id"] != task_id]

        deleted = len(tasks_db) < before

        if deleted:
            log_agent_event(
                "task_deleted",
                "task_tools",
                {"task_id": task_id},
            )

        return deleted

    @staticmethod
    def get_statistics() -> Dict:
        stats = {
            "total": len(tasks_db),
            "pending": len([t for t in tasks_db if t["status"] == "pending"]),
            "in_progress": len([t for t in tasks_db if t["status"] == "in_progress"]),
            "completed": len([t for t in tasks_db if t["status"] == "completed"]),
            "high_priority": len([t for t in tasks_db if t["priority"] == "high"]),
            "medium_priority": len([t for t in tasks_db if t["priority"] == "medium"]),
            "low_priority": len([t for t in tasks_db if t["priority"] == "low"]),
        }

        log_agent_event(
            "task_statistics_generated",
            "task_tools",
            stats,
        )

        return stats