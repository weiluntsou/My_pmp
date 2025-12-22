from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Engineer Schemas
class EngineerBase(BaseModel):
    name: str
    role: str = "Engineer"

class EngineerCreate(EngineerBase):
    pass

class Engineer(EngineerBase):
    id: int
    class Config:
        from_attributes = True

# Weekly Progress Schemas
class WeeklyProgressBase(BaseModel):
    week_number: int
    year: int
    planned_progress: float = 0
    actual_progress: float = 0
    planned_description: Optional[str] = None
    actual_description: Optional[str] = None
    actual_hours: Optional[float] = 0.0
    meeting_date: Optional[date] = None
    meeting_id: Optional[int] = None

class WeeklyProgressCreate(WeeklyProgressBase):
    pass

class WeeklyProgress(WeeklyProgressBase):
    id: int
    project_id: int
    class Config:
        from_attributes = True

# Project Update Schemas
class ProjectUpdateBase(BaseModel):
    project_id: int
    content: str
    status_snapshot: Optional[str] = None
    progress_snapshot: Optional[int] = None

class ProjectUpdateCreate(ProjectUpdateBase):
    meeting_id: Optional[int] = None

class ProjectUpdate(ProjectUpdateBase):
    id: int
    class Config:
        from_attributes = True

# Project Schemas
class ProjectLogBase(BaseModel):
    content: str

class ProjectLogCreate(ProjectLogBase):
    pass

class ProjectLog(ProjectLogBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MaintenanceLogBase(BaseModel):
    log_type: str
    content: str
    hours_spent: Optional[float] = 0.0
    log_date: Optional[date] = None

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLog(MaintenanceLogBase):
    id: int
    project_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    cft_unit: str
    request_unit: Optional[str] = None
    year: int
    status: str = "Planning"
    progress: int = 0
    description: Optional[str] = None
    duration_weeks: Optional[int] = 12
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    closure_date: Optional[date] = None
    kickoff_date: Optional[date] = None # Changed to date
    lead_engineer_id: Optional[int] = None
    meeting_day: Optional[str] = None
    meeting_time: Optional[str] = None
    
class ProjectCreate(ProjectBase):
    lead_engineer_name: Optional[str] = None # For Find or Create logic

class Project(ProjectBase):
    id: int
    status: str
    progress: int
    lead_engineer: Optional[Engineer] = None
    weekly_progress: List[WeeklyProgress] = []
    updates: List[ProjectUpdate] = []
    logs: List[ProjectLog] = [] # Added logs
    maintenance_logs: List[MaintenanceLog] = []
    class Config:
        from_attributes = True

# Meeting Schemas
class MeetingBase(BaseModel):
    date: date
    type: str # Weekly, Monthly
    title: str
    minutes_text: Optional[str] = None
    next_week_plan: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: int
    audio_path: Optional[str] = None
    class Config:
        from_attributes = True


