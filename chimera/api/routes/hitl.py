from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid

router = APIRouter()

class ReviewItem(BaseModel):
    task_id: str
    generated_content: Optional[str]
    confidence_score: float
    reasoning_trace: str

# In-memory mock queue for demonstration
mock_queue = [
    {
        "task_id": "task-001",
        "generated_content": "Hey guys! Check out the new Chimera sneakers dropping this Friday! #Chimera #Fashion",
        "confidence_score": 0.95,
        "reasoning_trace": "Content matches 'Excited/Hype' persona. No sensitive topics detected. High confidence."
    },
    {
        "task_id": "task-002",
        "generated_content": "I think the new policy on crypto regulation is fascinating. What do you imply?",
        "confidence_score": 0.75,
        "reasoning_trace": "Topic 'crypto regulation' flagged as potentially sensitive (Financial/Political). Confidence lowered due to ambiguity."
    },
    {
        "task_id": "task-003",
        "generated_content": "Buy this token now! It's going to the moon! 100x guaranteed!",
        "confidence_score": 0.45,
        "reasoning_trace": "CRITICAL: Detected 'Financial Advice' pattern. Direct promise of returns. Violates safety guidelines."
    }
]

@router.get("/queue", response_model=List[ReviewItem])
async def get_review_queue():
    """Fetches items pending human review."""
    return mock_queue

@router.post("/{task_id}/approve")
async def approve_task(task_id: str):
    """Approves a tasks and removes it from the queue."""
    global mock_queue
    # Find the task to ensure it exists
    task = next((t for t in mock_queue if t["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Simulate processing
    print(f"Task {task_id} APPROVED by user.")
    
    # Remove from queue
    mock_queue = [t for t in mock_queue if t["task_id"] != task_id]
    
    return {"status": "approved", "task_id": task_id}

@router.post("/{task_id}/reject")
async def reject_task(task_id: str):
    """Rejects a task."""
    global mock_queue
    task = next((t for t in mock_queue if t["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    print(f"Task {task_id} REJECTED by user.")
    mock_queue = [t for t in mock_queue if t["task_id"] != task_id]
    
    return {"status": "rejected", "task_id": task_id}
