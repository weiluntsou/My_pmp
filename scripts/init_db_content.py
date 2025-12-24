from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from datetime import date, timedelta

def init_content():
    db = SessionLocal()
    try:
        # 1. Check/Create Global Active Sprint
        active_sprint = db.query(models.Sprint).filter(
            models.Sprint.status == 'active',
            models.Sprint.project_id == None
        ).first()

        if not active_sprint:
            today = date.today()
            start = today - timedelta(days=today.weekday()) # Monday
            end = start + timedelta(days=12) # 2 Weeks (approx)
            
            print(f"Creating Global Active Sprint starting {start}...")
            active_sprint = models.Sprint(
                name=f"Global Sprint {today.strftime('%Y-W%W')}",
                start_date=start,
                end_date=end,
                status="active",
                project_id=None # Global
            )
            db.add(active_sprint)
            db.commit()
            db.refresh(active_sprint)
        else:
            print(f"Found active sprint: {active_sprint.name}")

        # 2. Sync Active Projects to Tasks
        # We look for projects that don't have a task in this sprint yet
        projects = db.query(models.Project).filter(
            models.Project.status.in_(['Planning', 'Development'])
        ).all()

        count = 0
        for proj in projects:
            # Check if task exists for this project in this sprint
            existing_task = db.query(models.Task).filter(
                models.Task.sprint_id == active_sprint.id,
                models.Task.project_id == proj.id
            ).first()

            if not existing_task:
                print(f"Creating task for project: {proj.name}")
                new_task = models.Task(
                    title=f"Project Execution: {proj.name}",
                    description=f"High-level tracking for project {proj.name}",
                    sprint_id=active_sprint.id,
                    project_id=proj.id,
                    assignee_id=proj.lead_engineer_id,
                    priority="High",
                    status="In Progress",
                    health="Green",
                    progress=proj.progress,
                    pm_note="Auto-generated from Project"
                )
                db.add(new_task)
                count += 1
        
        db.commit()
        print(f"Successfully created {count} tasks from active projects.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_content()
