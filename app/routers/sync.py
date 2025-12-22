from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from datetime import datetime
from typing import List, Optional
import io

router = APIRouter(
    prefix="/api/sync",
    tags=["sync"],
    responses={404: {"description": "Not found"}},
)

MARKDOWN_HEADER = "# PROJECT_EXPORT_v1"

def generate_markdown_content(projects: List[models.Project]) -> str:
    lines = [MARKDOWN_HEADER, ""]
    
    for p in projects:
        lines.append(f"## Project: {p.name}")
        lines.append(f"- ID: {p.id}")
        lines.append(f"- Year: {p.year}")
        lines.append(f"- CFT Unit: {p.cft_unit}")
        lines.append(f"- Status: {p.status}")
        lines.append(f"- Request Unit: {p.request_unit or ''}")
        lines.append(f"- Lead Engineer: {p.lead_engineer.name if p.lead_engineer else 'None'}")
        lines.append(f"- Description: {p.description or ''}")
        
        # Key Dates
        dates = []
        if p.start_date: dates.append(f"Start={p.start_date}")
        if p.kickoff_date: dates.append(f"Kickoff={p.kickoff_date}")
        if p.closure_date: dates.append(f"Closure={p.closure_date}")
        lines.append(f"- Key Dates: {', '.join(dates)}")
        
        # Schedule
        lines.append(f"- Schedule: Day=[{p.meeting_day or ''}], Time=[{p.meeting_time or ''}]")
        lines.append("")
        
        # Weekly Progress
        lines.append("### Weekly Progress")
        lines.append("| Week | Planned | Actual | Hours | Description |")
        lines.append("|------|---------|--------|-------|-------------|")
        # Sort by week
        wps = sorted(p.weekly_progress, key=lambda x: x.week_number)
        for wp in wps:
            desc = wp.actual_description or wp.planned_description or ""
            desc = desc.replace("\n", " ").replace("|", "/") # Sanitize for table
            lines.append(f"| {wp.week_number} | {wp.planned_progress} | {wp.actual_progress} | {wp.actual_hours} | {desc} |")
        lines.append("")
        
        # Meeting Logs/History
        lines.append("### Meeting Logs")
        # Combine ProjectLogs and Meeting updates if we had them linked, for now use ProjectLog
        logs = sorted(p.logs, key=lambda x: x.created_at, reverse=True)
        for log in logs:
            lines.append(f"- Date: {log.created_at.strftime('%Y-%m-%d')}")
            lines.append(f"- Content: {log.content}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
    return "\n".join(lines)

@router.post("/export")
def export_projects(project_ids: List[int], db: Session = Depends(get_db)):
    projects = db.query(models.Project).filter(models.Project.id.in_(project_ids)).all()
    content = generate_markdown_content(projects)
    
    # Generate Filename
    if len(projects) == 1:
        # Sanitize filename
        safe_name = "".join([c for c in projects[0].name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.md"
    else:
        filename = f"Projects_Export_{datetime.now().strftime('%Y%m%d')}.md"
        
    return {"content": content, "filename": filename}

@router.get("/template")
def get_template():
    content = f"""{MARKDOWN_HEADER}

## Project: Sample Project
- ID: New
- Year: 2025
- CFT Unit: Marketing
- Status: Planning
- Request Unit: Requirements Team
- Lead Engineer: John Doe
- Description: This is a sample project imported from LLM.
- Key Dates: Start=2025-01-01
- Schedule: Day=[Mon], Time=[10:00]

### Weekly Progress
| Week | Planned | Actual | Hours | Description |
|------|---------|--------|-------|-------------|
| 1    | 10      | 10     | 8     | Kickoff and Requirements |

### Meeting Logs
- Date: 2025-01-02
- Content: Initial meeting to discuss scope.
---
"""
    return {"content": content}

@router.post("/import")
async def import_projects(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
        
    if not text_content.startswith(MARKDOWN_HEADER):
        raise HTTPException(status_code=400, detail="Invalid file format. Header missing.")
        
    # Robust Parsing Logic using Regex
    import re
    # Split by line that starts with "## Project: "
    # The first element [0] will be the header/preamble, subsequent are projects
    projects_data = re.split(r'^## Project: ', text_content, flags=re.MULTILINE)
    
    log_messages = []
    
    for p_chunk in projects_data[1:]: # Skip preamble
        if not p_chunk.strip(): continue # Skip empty chunks
        
        lines = p_chunk.strip().split("\n")
        name = lines[0].strip()
        
        # Extract basic info
        info = {}
        current_section = "info"
        weekly_progress_rows = []
        logs = []
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("### Weekly Progress"):
                current_section = "weekly"
                continue
            elif line.startswith("### Meeting Logs"):
                current_section = "logs"
                continue
            # elif line.startswith("---"):
            #    break 
            # User uses --- as separator between logs, so we should NOT break. 
            # The split by "## Project:" handles the main separation.
                
            if current_section == "info":
                clean_line = line.lstrip("-* ").strip()
                if clean_line.startswith("ID:"): info['id'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Year:"): info['year'] = int(clean_line.split(":", 1)[1].strip())
                elif clean_line.startswith("CFT Unit:"): info['cft'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Status:"): info['status'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Request Unit:"): info['request_unit'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("需求窗口:"): info['request_unit'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Lead Engineer:"): info['lead'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Description:"): info['desc'] = clean_line.split(":", 1)[1].strip()
                elif clean_line.startswith("Key Dates:"): 
                    parts = clean_line.split(":", 1)[1].split(",")
                    for p in parts:
                        if "=" in p:
                            k, v = p.split("=")
                            info[k.strip()] = v.strip()
                elif clean_line.startswith("Schedule:"):
                    # Day=[Mon], Time=[10:00]
                    # import re is already imported
                    m_day = re.search(r"Day=\[(.*?)\]", line)
                    m_time = re.search(r"Time=\[(.*?)\]", line)
                    if m_day: info['meeting_day'] = m_day.group(1)
                    if m_time: info['meeting_time'] = m_time.group(1)

            elif current_section == "weekly":
                if line.startswith("|") and not "Planned" in line and not line.startswith("|--") and not line.startswith("| --"):
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cols) >= 5:
                        def safe_float(val):
                            try:
                                return float(val)
                            except ValueError:
                                return 0.0
                        
                        weekly_progress_rows.append({
                            "week": int(safe_float(cols[0])), # Handle potential parsing error or row mismatch
                            "planned": safe_float(cols[1]),
                            "actual": safe_float(cols[2]),
                            "hours": safe_float(cols[3]), # Handle '-'
                            "desc": cols[4]
                        })

            elif current_section == "logs":
                clean_line = line.lstrip("-* ").strip()
                if clean_line.startswith("Date:"):
                    logs.append({"date": clean_line.split(":", 1)[1].strip(), "content": ""})
                elif clean_line.startswith("Content:"):
                    if logs: logs[-1]["content"] = clean_line.split(":", 1)[1].strip()
                elif logs and line and not line.strip().startswith("-") and not line.strip().startswith("*"):
                    # Append multiline content
                    logs[-1]["content"] += " " + line.strip()

        # Database Update Logic
        # 1. Find or Create Engineer
        lead_id = None
        if info.get('lead') and info['lead'] != 'None':
            eng = db.query(models.Engineer).filter(models.Engineer.name == info['lead']).first()
            if not eng:
                eng = models.Engineer(name=info['lead'])
                db.add(eng)
                db.commit()
                db.refresh(eng)
            lead_id = eng.id
            
        # 2. Find or Create Project
        project = None
        if info.get('id') and info['id'] != 'New':
            try:
                db_id = int(info['id'])
                project = db.query(models.Project).filter(models.Project.id == db_id).first()
            except ValueError:
                # ID is not an integer (e.g., custom code), skip ID lookup
                pass
        
        # Fallback: Find by Name if ID lookup failed or wasn't applicable
        if not project:
            project = db.query(models.Project).filter(models.Project.name == name).first()
        
        if not project:
            # Create
            project = models.Project(
                name=name,
                year=info.get('year', 2025),
                cft_unit=info.get('cft', 'Unknown'),
                request_unit=info.get('request_unit'),
                status=info.get('status', 'Planning'),
                description=info.get('desc'),
                lead_engineer_id=lead_id
            )
            
            # If the ID was a custom string, maybe append it to description? 
            # For now, we mainly want to avoid crashing.
            
            db.add(project)
            db.commit()
            db.refresh(project)
            log_messages.append(f"Created Project: {name}")
        else:
            # Update basic fields
            project.cft_unit = info.get('cft', project.cft_unit)
            if info.get('request_unit'):
                project.request_unit = info['request_unit']
            project.status = info.get('status', project.status)
            project.description = info.get('desc', project.description)
            project.lead_engineer_id = lead_id
            log_messages.append(f"Updated Project: {name}")
            
        # Update extra fields
        if 'Start' in info: project.start_date = datetime.strptime(info['Start'], '%Y-%m-%d').date()
        if 'Kickoff' in info: project.kickoff_date = datetime.strptime(info['Kickoff'], '%Y-%m-%d').date()
        if 'Closure' in info: project.closure_date = datetime.strptime(info['Closure'], '%Y-%m-%d').date()
        if 'meeting_day' in info: project.meeting_day = info['meeting_day']
        if 'meeting_time' in info: project.meeting_time = info['meeting_time']
        
        db.commit()
        
        # 3. Update Weekly Progress
        for row in weekly_progress_rows:
            wp = db.query(models.WeeklyProgress).filter(
                models.WeeklyProgress.project_id == project.id,
                models.WeeklyProgress.week_number == row['week']
            ).first()
            
            if wp:
                wp.planned_progress = row['planned']
                wp.actual_progress = row['actual']
                wp.actual_hours = row['hours']
                if row['actual'] > 0:
                     wp.actual_description = row['desc']
                else:
                     wp.planned_description = row['desc']
            else:
                wp = models.WeeklyProgress(
                    project_id=project.id,
                    week_number=row['week'],
                    year=project.year,
                    planned_progress=row['planned'],
                    actual_progress=row['actual'],
                    actual_hours=row['hours'],
                    planned_description=row['desc']
                )
                db.add(wp)
        db.commit()
        
        # 4. Import Logs (Check duplicates)
        for log in logs:
            # Simple deduplication by date + beginning of content
            exists = db.query(models.ProjectLog).filter(
                models.ProjectLog.project_id == project.id,
                models.ProjectLog.content.like(f"%{log['content'][:20]}%") # Rough check
            ).first()
            
            if not exists:
                new_log = models.ProjectLog(
                    project_id=project.id,
                    content=f"[Imported] {log['content']}"
                )
                # Try to set date? ProjectLog uses created_at which is DateTime.
                # We can't strictly force it without a hack or schema change, so just append.
                # Or we can store the date in the content.
                new_log.content = f"[{log['date']}] {log['content']}"
                db.add(new_log)
                
            # Sync to Weekly Progress (Actual Description)
            try:
                log_date = datetime.strptime(log['date'], '%Y-%m-%d').date()
                # ISO Week
                iso_year, iso_week, _ = log_date.isocalendar()
                
                # Check if this week exists in WeeklyProgress
                wp_sync = db.query(models.WeeklyProgress).filter(
                    models.WeeklyProgress.project_id == project.id,
                    models.WeeklyProgress.week_number == iso_week,
                    models.WeeklyProgress.year == iso_year
                ).first()
                
                if wp_sync:
                    # Append if not present to avoid duplication if running import multiple times
                    # Simple check if content is already in description
                    current_desc = wp_sync.actual_description or ""
                    # We add a marker or just checking text similarity?
                    # User request: "Meeting records should also sync to project actual progress"
                    # Let's prepend or append carefully.
                    
                    # If the description is empty, just fill it.
                    if not current_desc:
                        wp_sync.actual_description = f"[Meeting {log['date']}] {log['content']}"
                    elif log['content'] not in current_desc:
                        # Append
                        wp_sync.actual_description = f"{current_desc}\n[Meeting {log['date']}] {log['content']}"
                else:
                    # Option: Create the week if it doesn't exist? 
                    # User markdown table might miss weeks but have logs.
                    # Create it.
                    wp_sync = models.WeeklyProgress(
                        project_id=project.id,
                        week_number=iso_week,
                        year=iso_year,
                        planned_progress=0, # Unknown
                        actual_progress=0, # Unknown, just logging info
                        actual_description=f"[Meeting {log['date']}] {log['content']}"
                    )
                    db.add(wp_sync)
                    
            except ValueError:
                pass # Invalid date format, skip sync
                
        db.commit()
        db.commit()

    return {"status": "success", "logs": log_messages}
