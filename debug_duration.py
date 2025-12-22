from app.database import SessionLocal
from app import models
from sqlalchemy import func

db = SessionLocal()
project_id = 1 # Assuming project 1 from user log

try:
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        print(f"Project ID: {project.id}")
        print(f"Stored Duration: {project.duration_weeks}")
        
        max_week = db.query(func.max(models.WeeklyProgress.week_number)).filter(models.WeeklyProgress.project_id == project_id).scalar()
        print(f"Max WeeklyProgress Week: {max_week}")
        
        if max_week and max_week > (project.duration_weeks or 0):
            print("MISMATCH DETECTED: Max week > Stored Duration")
    else:
        print("Project not found")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
