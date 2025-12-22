from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Float, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Engineer(Base):
    __tablename__ = "engineers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    role = Column(String, default="Engineer")
    
    projects = relationship("Project", back_populates="lead_engineer")

class ProjectLog(Base):
    __tablename__ = "project_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="logs")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    log_type = Column(String) # "System Maintenance", "Data Patch", "Routine Check"
    content = Column(String)
    hours_spent = Column(Float, default=0.0)
    log_date = Column(Date, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="maintenance_logs")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cft_unit = Column(String, index=True)  # Which CFT requested it
    request_unit = Column(String, nullable=True) # Demand Contact Unit
    year = Column(Integer, index=True)
    duration_weeks = Column(Integer, default=12) # New field
    status = Column(String, default="Planning") # Planning, Development, Testing, Complete
    progress = Column(Integer, default=0) # 0-100
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    closure_date = Column(Date, nullable=True) # Date moved to maintenance
    kickoff_date = Column(Date, nullable=True)
    
    # Meeting Recurrence
    meeting_day = Column(String, nullable=True) # Mon, Tue, Wed, Thu, Fri
    meeting_time = Column(String, nullable=True) # HH:MM
    
    lead_engineer_id = Column(Integer, ForeignKey("engineers.id"), nullable=True)
    lead_engineer = relationship("Engineer", back_populates="projects")
    updates = relationship("ProjectUpdate", back_populates="project", cascade="all, delete-orphan")
    weekly_progress = relationship("WeeklyProgress", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("ProjectLog", back_populates="project", order_by="desc(ProjectLog.created_at)", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="project", order_by="desc(MaintenanceLog.log_date)", cascade="all, delete-orphan")

class WeeklyProgress(Base):
    __tablename__ = "weekly_progress"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    week_number = Column(Integer)
    year = Column(Integer)
    planned_progress = Column(Integer, default=0) # Percentage 0-100
    actual_progress = Column(Integer, default=0) # Percentage 0-100
    planned_description = Column(String)
    actual_description = Column(String, nullable=True)
    actual_hours = Column(Float, default=0.0)
    meeting_date = Column(Date, nullable=True) # Actual date of the meeting/log
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True) # Linked meeting for verification
    
    project = relationship("Project", back_populates="weekly_progress")
    meeting = relationship("Meeting")

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    type = Column(String) # Weekly, Monthly, Adhoc
    title = Column(String)
    audio_path = Column(String, nullable=True)
    minutes_text = Column(Text, nullable=True) # The actual content
    next_week_plan = Column(Text, nullable=True) # For weekly meetings
    
    updates = relationship("ProjectUpdate", back_populates="meeting")

class ProjectUpdate(Base):
    __tablename__ = "project_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    
    content = Column(Text) # What happened for this project in this context
    status_snapshot = Column(String, nullable=True) # Snapshot of status at this time
    progress_snapshot = Column(Integer, nullable=True)

    project = relationship("Project", back_populates="updates")
    meeting = relationship("Meeting", back_populates="updates")
