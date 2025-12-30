from app.database import SessionLocal, engine
from app import models
from sqlalchemy import text

db = SessionLocal()

def add_column(table, column, type_def, default_val=None):
    try:
        with engine.connect() as conn:
            default_clause = f"DEFAULT {default_val}" if default_val is not None else ""
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_def} {default_clause}"))
            conn.commit()
            print(f"Added {column} to {table}")
    except Exception as e:
        print(f"Column {column} likely exists or error: {e}")

# Add columns
add_column("weekly_progress", "actual_hours", "FLOAT", "0")
add_column("maintenance_logs", "hours_spent", "FLOAT", "0")
add_column("projects", "meeting_day", "VARCHAR")
add_column("projects", "meeting_time", "VARCHAR")
add_column("projects", "predicted_end_date", "DATE")

print("Migration complete.")
