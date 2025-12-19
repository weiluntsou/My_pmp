from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).options(joinedload(models.Project.lead_engineer)).offset(skip).limit(limit).all()
    return projects

# Engineer endpoints (Simple version inside projects router for now)
# Defined BEFORE generic ID routes to avoid matching confusion
@router.post("/engineers", response_model=schemas.Engineer)
def create_engineer(engineer: schemas.EngineerCreate, db: Session = Depends(get_db)):
    db_engineer = models.Engineer(**engineer.dict())
    db.add(db_engineer)
    db.commit()
    db.refresh(db_engineer)
    return db_engineer

@router.get("/engineers", response_model=List[schemas.Engineer])
def read_engineers(db: Session = Depends(get_db)):
    return db.query(models.Engineer).all()

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"ok": True}

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project_data = project.dict()
    lead_name = project_data.pop("lead_engineer_name", None)

    if lead_name:
        lead_name = lead_name.strip()
        # Check if engineer exists
        engineer = db.query(models.Engineer).filter(models.Engineer.name == lead_name).first()
        if not engineer:
            engineer = models.Engineer(name=lead_name)
            db.add(engineer)
            db.commit()
            db.refresh(engineer)
        project_data["lead_engineer_id"] = engineer.id

    db_project = models.Project(**project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Initialize Weekly Progress
    duration = project.duration_weeks or 12
    
    # Calculate distribution (100% total)
    base_progress = 100 // duration
    remainder = 100 % duration

    # Determine project type
    name_lower = db_project.name.lower().replace(" ", "")
    is_standard_dev = "phase" not in name_lower or "phase1" in name_lower

    for w in range(1, duration + 1):
        # Distribute evenly, add remainder to last week
        planned = base_progress
        if w == duration:
            planned += remainder
        
        # Determine Description
        description = "Planned"
        remaining_weeks = duration - w
        
        # Logic: last 3 weeks for Testing/Correction
        is_last_stage = remaining_weeks < 3

        if is_standard_dev:
            # Standard Cycle: Reqs/Arch -> UI/Proto -> Dev -> Test
            if is_last_stage:
                description = "UAT測試與錯誤修正"
            elif w <= 2:
                description = "需求確認與架構討論"
            elif w <= 4:
                description = "UI/UX設計與資料庫規劃"
            else:
                description = "核心功能開發與實作"
        else:
            # Optimization Cycle: Optimization -> Test
            if is_last_stage:
                 description = "UAT測試與錯誤修正"
            else:
                 description = "系統優化與效能調校"

        wp = models.WeeklyProgress(
            project_id=db_project.id,
            week_number=w,
            year=project.year,
            planned_progress=planned,
            actual_progress=0,
            planned_description=description
        )
        db.add(wp)
    db.commit()
    
    return db_project

@router.post("/{project_id}/plan", response_model=List[schemas.WeeklyProgress])
def update_project_plan(project_id: int, plans: List[schemas.WeeklyProgressCreate], db: Session = Depends(get_db)):
    try:
        # Batch update planned progress
        response = []
        for plan in plans:
            # Find existing or create
            wp = db.query(models.WeeklyProgress).filter(
                models.WeeklyProgress.project_id == project_id,
                models.WeeklyProgress.week_number == plan.week_number
            ).first()
            
            if wp:
                wp.planned_progress = plan.planned_progress
                wp.planned_description = plan.planned_description # Update description
                # Only update actual if provided effectively (optional logic)
            else:
                 wp = models.WeeklyProgress(**plan.dict(), project_id=project_id)
                 db.add(wp)
            response.append(wp)
        
        db.commit()
        
        # Refresh all objects to ensure they are ready for serialization
        for item in response:
            db.refresh(item)
            
        return response
    except Exception as e:
        print(f"Error updating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.post("/{project_id}/updates", response_model=schemas.ProjectUpdate)
def create_project_update(project_id: int, update: schemas.ProjectUpdateCreate, db: Session = Depends(get_db)):
    # Verify project exists
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_update = models.ProjectUpdate(**update.dict())
    db.add(db_update)
    
    # Optionally update project status/progress if provided
    if update.status_snapshot:
        db_project.status = update.status_snapshot
    if update.progress_snapshot is not None:
        db_project.progress = update.progress_snapshot
        
    db.commit()
    db.refresh(db_update)
    return db_update



@router.post("/{project_id}/weekly_progress", response_model=schemas.WeeklyProgress)
def create_weekly_progress(project_id: int, progress: schemas.WeeklyProgressCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if entry exists
    db_progress = db.query(models.WeeklyProgress).filter(
        models.WeeklyProgress.project_id == project_id,
        models.WeeklyProgress.week_number == progress.week_number,
        models.WeeklyProgress.year == progress.year
    ).first()
    
    if db_progress:
        # Update existing
        # Use exclude_unset=True to prevent overwriting fields like planned_progress with defaults if not sent
        for key, value in progress.dict(exclude_unset=True).items():
            setattr(db_progress, key, value)
    else:
        # Create new
        db_progress = models.WeeklyProgress(**progress.dict(), project_id=project_id)
        db.add(db_progress)

    db.commit()
    
    # Recalculate Project Total Progress
    # Sum of PLANNED progress for weeks that have an actual description (indicating it's done/reported)
    # Filter for non-empty actual_description
    total_progress = 0
    all_weeks = db.query(models.WeeklyProgress).filter(models.WeeklyProgress.project_id == project_id).all()
    
    for w in all_weeks:
        if w.actual_description and len(w.actual_description.strip()) > 0:
            total_progress += w.planned_progress

    db_project.progress = total_progress
    
    # Auto-advance status if progress started
    if db_project.status == "Planning" and total_progress > 0:
        db_project.status = "Development"
    
    # Log update
    log_content = f"Updated Week {progress.week_number}: {progress.actual_description or ''} (Progress: {total_progress}%, Hours: {progress.actual_hours or 0})"
    log_entry = models.ProjectLog(project_id=project_id, content=log_content)
    db.add(log_entry)
    
    db.commit()
    
    db.refresh(db_progress)
    return db_progress

@router.post("/{project_id}/close", response_model=schemas.Project)
def close_project(project_id: int, closure_date: str = None, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse date
    from datetime import datetime
    try:
        c_date = datetime.strptime(closure_date, '%Y-%m-%d').date() if closure_date else None
    except:
        c_date = None

    db_project.status = "Maintenance"
    db_project.closure_date = c_date
    db.commit()
    db.refresh(db_project)
    
    # Log
    log = models.ProjectLog(project_id=project_id, content=f"Project Closed and moved to Maintenance. Closure Date: {closure_date}")
    db.add(log)
    db.commit()
    
    return db_project

@router.post("/{project_id}/maintenance", response_model=schemas.MaintenanceLog)
def create_maintenance_log(project_id: int, log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_log = models.MaintenanceLog(**log.dict(), project_id=project_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # Also add to main project history log for visibility
    main_log = models.ProjectLog(project_id=project_id, content=f"[{log.log_type}] {log.content} (Hours: {log.hours_spent})")
    db.add(main_log)
    db.commit()
    
    return db_log
