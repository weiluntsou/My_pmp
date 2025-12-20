from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from datetime import datetime, date, timedelta

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

@router.get("/generate")
def generate_report(type: str, year: int, period: int = 1, db: Session = Depends(get_db)):
    """
    type: 'weekly', 'monthly', 'spring_keynote', 'autumn_keynote'
    period: week_number for weekly, month_number for monthly. Ignored for keynotes.
    """
    
    report_lines = []
    
    if type == 'weekly':
        report_lines.append(f"# Weekly Report - Week {period}, {year}")
        report_lines.append("")
        
        # Get WeeklyProgress for this week
        wps = db.query(models.WeeklyProgress).filter(
            models.WeeklyProgress.year == year,
            models.WeeklyProgress.week_number == period
        ).all()
        
        # Group by Project
        projects_map = {}
        for wp in wps:
            # Only include if there's actual activity or if it's planned
            if wp.actual_description or wp.planned_description:
                 projects_map[wp.project_id] = wp
        
        report_lines.append(f"## Summary")
        report_lines.append(f"Total Active Projects: {len(projects_map)}")
        report_lines.append("")
        
        for pid, wp in projects_map.items():
            project = db.query(models.Project).get(pid)
            if not project: continue
            
            report_lines.append(f"### {project.name} ({project.status})")
            if wp.actual_description:
                report_lines.append(f"- **Actual**: {wp.actual_description}")
            else:
                report_lines.append(f"- *Planned*: {wp.planned_description}")
            
            if wp.actual_hours > 0:
                report_lines.append(f"- Hours: {wp.actual_hours}")
            report_lines.append("")

    elif type == 'monthly':
        report_lines.append(f"# Monthly Report - {year}-{period:02d}")
        report_lines.append("")
        
        # Logic: Find projects with WeeklyProgress in this month
        # Approximate: Week 1-4, 5-8 etc? Or by specific date range?
        # Better: Filter Logs by date range 
        start_date = date(year, period, 1)
        if period == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, period + 1, 1)
            
        logs = db.query(models.ProjectLog).filter(
            models.ProjectLog.created_at >= start_date,
            models.ProjectLog.created_at < end_date
        ).all()
        
        grouped_logs = {}
        for log in logs:
            if log.project_id not in grouped_logs: grouped_logs[log.project_id] = []
            grouped_logs[log.project_id].append(log)
            
        for pid, p_logs in grouped_logs.items():
            project = db.query(models.Project).get(pid)
            if not project: continue
            
            report_lines.append(f"### {project.name}")
            for l in p_logs:
                # Clean content
                content = l.content.replace("[Imported]", "").strip()
                report_lines.append(f"- [{l.created_at.strftime('%Y-%m-%d')}] {content}")
            report_lines.append("")

    elif type in ['spring_keynote', 'autumn_keynote']:
        title = "Spring Keynote" if type == 'spring_keynote' else "Autumn Keynote"
        report_lines.append(f"# {title} {year}")
        
        # Date Ranges
        # Spring: Oct (prev year) - Mar (curr year)
        # Autumn: Apr (curr year) - Sep (curr year)
        
        if type == 'spring_keynote':
            start_date = date(year - 1, 10, 1)
            end_date = date(year, 4, 1)
        else:
            start_date = date(year, 4, 1)
            end_date = date(year, 10, 1)
            
        report_lines.append(f"Period: {start_date} to {end_date}")
        report_lines.append("")
        
        # Find projects completed or having major milestones in this period?
        # Let's find projects closed in this period OR with status Completed/Maintenance
        # and maybe major features delivered.
        
        # Simplified: List all projects that were Active or Completed during this time.
        # We can look at projects updated in this timeframe (Logs)
        
        relevant_pids = set()
        logs_in_range = db.query(models.ProjectLog).filter(
            models.ProjectLog.created_at >= start_date,
            models.ProjectLog.created_at < end_date
        ).all()
        for l in logs_in_range:
            relevant_pids.add(l.project_id)
            
        projects = db.query(models.Project).filter(models.Project.id.in_(relevant_pids)).all()
        
        report_lines.append("## Project Highlights")
        
        for p in projects:
            report_lines.append(f"### {p.name}")
            report_lines.append(f"**Status**: {p.status}")
            if p.closure_date:
                report_lines.append(f"**Closed**: {p.closure_date}")
            report_lines.append(f"**Description**: {p.description}")
            
            # Summarize activity?
            # Maybe count items completed? For now just list them.
            report_lines.append("")
            
    return {"content": "\n".join(report_lines)}
