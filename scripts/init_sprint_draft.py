from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from datetime import date, timedelta

def init_sprint_data():
    db = SessionLocal()
    try:
        # 1. Create Active Sprint if none exists
        active_sprint = db.query(models.Sprint).filter(models.Sprint.status == 'active').first()
        if not active_sprint:
            print("Creating new Active Sprint...")
            today = date.today()
            # Find Monday
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=13) # 2 weeks sprint
            
            active_sprint = models.Sprint(
                name=f"Sprint {today.strftime('%Y-%W')}",
                start_date=start,
                end_date=end,
                status="active",
                project_id=None # Sprints might count as global if project_id is nullable? 
                # Checking models.py: project_id = Column(Integer, ForeignKey("projects.id"))
                # Wait, if Sprint belongs to A project, then we can't have a "Global Sprint" containing tasks from multiple projects.
                # Let's check the model definition again.
            )
            # If Sprint requires a project_id, my design of "Global War Room" is flawed or assumes one "Meta Project".
            # Let's check models.py content again.
            pass

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_sprint_data()
