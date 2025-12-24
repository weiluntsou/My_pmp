from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.database import get_db
from app import models, schemas
from datetime import date

router = APIRouter(
    prefix="/pm",
    tags=["pm_tools"],
    responses={404: {"description": "Not found"}},
)

@router.patch("/tasks/batch")
async def batch_update_tasks(updates: List[schemas.TaskBatchUpdateItem], db: Session = Depends(get_db)):
    """
    Update multiple tasks in a single transaction.
    """
    updated_count = 0
    errors = []

    try:
        for item in updates:
            task = db.query(models.Task).filter(models.Task.id == item.id).first()
            if not task:
                errors.append(f"Task ID {item.id} not found")
                continue
            
            # Update fields if provided
            update_data = item.dict(exclude_unset=True)
            # Remove id from update data if present (it shouldn't be updated)
            if 'id' in update_data:
                del update_data['id']
            
            for key, value in update_data.items():
                setattr(task, key, value)
            
            updated_count += 1
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Batch update processed",
        "updated_count": updated_count,
        "errors": errors
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated stats for the current active sprint (or all active tasks if no sprint active).
    """
    today = date.today()
    
    # 1. Find Active Sprint
    # Prioritize explicitly active, then date-based
    active_sprint = db.query(models.Sprint).filter(models.Sprint.status == 'active').first()
    
    if not active_sprint:
        # Fallback: Find sprint covering today
        active_sprint = db.query(models.Sprint).filter(
            models.Sprint.start_date <= today,
            models.Sprint.end_date >= today
        ).first()

    # Base Query
    query = db.query(models.Task)
    if active_sprint:
        query = query.filter(models.Task.sprint_id == active_sprint.id)
    else:
        # If no active sprint, maybe just show all or a specific fallback?
        # Let's show all tasks that are NOT Done if no sprint context
        pass 

    tasks = query.all()

    # 2. Aggregations
    total_tasks = len(tasks)
    
    # Avg Progress
    avg_progress = 0
    if total_tasks > 0:
        total_p = sum(t.progress for t in tasks)
        avg_progress = round(total_p / total_tasks, 1)

    # Health Counts & Status Counts
    health_counts = {"Green": 0, "Yellow": 0, "Red": 0}
    status_counts = {"Todo": 0, "In Progress": 0, "Done": 0}
    risk_items = []

    for t in tasks:
        # Health
        h = t.health or "Green"
        if h in health_counts:
            health_counts[h] += 1
        else:
            health_counts[h] = 1
            
        # Status
        s = t.status or "Todo"
        if s in status_counts:
            status_counts[s] += 1
        else:
            status_counts[s] = 1

        if h in ["Yellow", "Red"]:
            risk_items.append({
                "title": t.title,
                "pm_note": t.pm_note,
                "assignee": t.assignee.name if t.assignee else "Unassigned",
                "health": h
            })

    return {
        "sprint": active_sprint.name if active_sprint else "No Active Sprint",
        "total_tasks": total_tasks,
        "avg_progress": avg_progress,
        "health_counts": health_counts,
        "status_counts": status_counts,
        "risk_items": risk_items
    }

from fastapi import Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard")
async def dashboard_view(request: Request):
    """
    Render the Command Dashboard.
    """
    return templates.TemplateResponse("pm/dashboard.html", {
        "request": request
    })

@router.get("/assessment")
async def assessment_view(request: Request, db: Session = Depends(get_db)):
    """
    Render the Rapid Assessment Grid.
    """
    today = date.today()
    active_sprint = db.query(models.Sprint).filter(models.Sprint.status == 'active').first()
    
    if not active_sprint:
        active_sprint = db.query(models.Sprint).filter(
            models.Sprint.start_date <= today,
            models.Sprint.end_date >= today
        ).first()
        
    query = db.query(models.Task)
    if active_sprint:
        query = query.filter(models.Task.sprint_id == active_sprint.id)
    
    tasks = query.all()
    
    # Serialize tasks (or pass objects if template can handle)
    # Jinja handles SQLAlchemy objects fine usually.
    
    return templates.TemplateResponse("pm/assessment.html", {
        "request": request,
        "tasks": tasks,
        "sprint": active_sprint
    })
