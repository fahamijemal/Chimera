from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
import datetime
from enum import Enum

class TaskType(str, Enum):
    GENERATE_CONTENT = "generate_content"
    SOCIAL_ACTION = "social_action"
    TRANSACTION = "transaction"

class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    REVIEW = "review"
    COMPLETE = "complete"
    FAILED = "failed"

class TaskContext(BaseModel):
    goal_description: str
    persona_constraints: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    context: TaskContext
    assigned_worker_id: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    status: TaskStatus = TaskStatus.PENDING

class TaskResult(BaseModel):
    task_id: str
    worker_id: str
    output: Dict[str, Any]
    confidence_score: float = 0.0
    status: str = "success"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
