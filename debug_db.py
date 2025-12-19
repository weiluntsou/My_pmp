from app.database import SessionLocal
from app import models

db = SessionLocal()

print("--- ENGINEERS ---")
engineers = db.query(models.Engineer).all()
for e in engineers:
    print(f"ID: {e.id}, Name: '{e.name}'")

print("\n--- PROJECTS ---")
projects = db.query(models.Project).all()
for p in projects:
    lead = p.lead_engineer.name if p.lead_engineer else "None"
    print(f"ID: {p.id}, Name: '{p.name}', Status: {p.status}, Lead: {lead}, LeadID: {p.lead_engineer_id}")

print("\n--- WEEKLY PROGRESS ---")
progress = db.query(models.WeeklyProgress).all()
print(f"Total Progress Records: {len(progress)}")
