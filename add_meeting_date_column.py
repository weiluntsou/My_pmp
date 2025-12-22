from app.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE weekly_progress ADD COLUMN meeting_date DATE"))
            print("Successfully added meeting_date column.")
        except Exception as e:
            print(f"Migration failed (Column might already exist?): {e}")

if __name__ == "__main__":
    migrate()
