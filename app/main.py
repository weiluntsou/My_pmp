from fastapi import FastAPI, Request, Depends, HTTPException
from datetime import date, datetime
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.routers import projects, meetings, sync, reports, pm_tools
from app.database import engine, Base, get_db
from app import models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevManage-Tech", description="Digital Development Section Project Management")

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(projects.router)
app.include_router(meetings.router)
app.include_router(sync.router)
app.include_router(reports.router)
app.include_router(pm_tools.router)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "page_title": "Dashboard"})

@app.get("/cft_projects", response_class=HTMLResponse)
async def cft_projects(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request, "page_title": "專案列表"})

@app.get("/meetings", response_class=HTMLResponse)
async def meetings_page(request: Request):
    return templates.TemplateResponse("meetings.html", {"request": request, "page_title": "會議規劃及紀錄"})

@app.get("/import_export", response_class=HTMLResponse)
async def read_import_export(request: Request):
    return templates.TemplateResponse("import_export.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def read_reports(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "page_title": "定期報告"})

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, view_mode: str = "week", focus_date: str = None, db: Session = Depends(get_db)):
    from app.utils import calculate_timeline, calculate_grid_position, get_iso_week_start
    from datetime import date, datetime, timedelta

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return HTMLResponse("Project not found", status_code=404)
    
    # 1. Handle Focus Date
    if focus_date:
        try:
            f_date = datetime.strptime(focus_date, "%Y-%m-%d").date()
        except:
            f_date = date.today()
    else:
        f_date = date.today()

    # 2. Calculate Timeline Metadata
    timeline = calculate_timeline(view_mode, f_date)
    
    # 3. Fetch Data & Group into "Gantt Bars" (Phases)
    weekly_data = db.query(models.WeeklyProgress).filter(models.WeeklyProgress.project_id == project_id).order_by(models.WeeklyProgress.week_number).all()
    
    gantt_bars = []
    current_bar = None
    
    # Sort just in case
    # weekly_data is sorted by week_number.
    
    for w in weekly_data:
        # Calculate Week's Date Range based on Project Year
        # Assuming ISO weeks:
        # Simple approximation: Jan 1st + (weeks-1)*7
        # Better: use project.year
        pyear = project.year or f_date.year
        # We need a robust week->date generic function. 
        # For this prototype, I'll use simple ISO calculation:
        # Jan 4th is always in week 1
        jan4 = date(pyear, 1, 4)
        start_of_year = jan4 - timedelta(days=jan4.weekday()) # Monday of Week 1
        week_start = start_of_year + timedelta(weeks=w.week_number - 1)
        week_end = week_start + timedelta(days=6)
        
        # Grouping Logic: Same Description + Consecutive
        desc = w.planned_description
        
        if current_bar and current_bar['name'] == desc and (week_start - current_bar['end']).days <= 7:
            # Extend current bar
            current_bar['end'] = week_end
            current_bar['weeks'].append(w)
        else:
            # Finish prev bar
            if current_bar:
                gantt_bars.append(current_bar)
            
            # Start new bar
            current_bar = {
                "name": desc,
                "start": week_start,
                "end": week_end,
                "weeks": [w],
                "status": "Planned" # Could derive from actual vs planned
            }
            
    if current_bar:
        gantt_bars.append(current_bar)

    # 4. Calculate Grid Positions for Bars
    final_bars = []
    for bar in gantt_bars:
        # Clamp dates or calculate positions? 
        # calculate_grid_position returns indices relative to View Start.
        # If bars are WAY out, indices will be negative or > total_units.
        start_idx, span = calculate_grid_position(bar['start'], bar['end'], timeline['start_date'], view_mode)
        
        # Check if visible
        # Visible if EndIdx >= 1 AND StartIdx <= Total
        end_idx = start_idx + span - 1
        if end_idx >= 1 and start_idx <= timeline['total_units']:
            # Clip for display if needed, but CSS Grid handles overflow hidden often.
            # However, simpler to clamp Start to 1 if < 1, and adjust span
            
            visible_start = max(1, start_idx)
            # Reduction in start means reduction in span
            # If start_idx was -5 (6 units left), and we became 1, we cut 6 units.
            # span should reduce by (visible_start - start_idx) if start_idx < 1?
            # Actually, standard grid approach:
            # grid-column: start / span check.
            
            bar['grid_start'] = start_idx
            bar['grid_span'] = span

            # 5. Calculate Actuals Positions (Per Week)
            bar['actuals'] = []
            for w in bar['weeks']:
                # Re-calculate dates for this specific week
                # (Logic matches the grouping loop)
                pyear = project.year or f_date.year
                jan4 = date(pyear, 1, 4)
                start_of_year = jan4 - timedelta(days=jan4.weekday())
                w_start = start_of_year + timedelta(weeks=w.week_number - 1)
                w_end = w_start + timedelta(days=6)
                
                a_start, a_span = calculate_grid_position(w_start, w_end, timeline['start_date'], view_mode)
                
                # Check visibility
                if a_start is not None:
                    a_end_idx = a_start + a_span - 1
                    if a_end_idx >= 1 and a_start <= timeline['total_units']:
                        bar['actuals'].append({
                            'grid_start': a_start,
                            'grid_span': a_span,
                            'progress': w.actual_progress,
                            'description': w.actual_description,
                            'week': w.week_number,
                            'year': w.year,
                            'actual_hours': w.actual_hours,
                            'planned_progress': w.planned_progress,
                            'planned_description': w.planned_description,
                            'has_content': bool(w.actual_description or w.actual_progress > 0)
                        })

            final_bars.append(bar)

    # Serialize safely for other parts of template
    safe_weekly_data = []
    for w in weekly_data:
        d = w.__dict__.copy()
        if "_sa_instance_state" in d: del d["_sa_instance_state"]
        # Handle date serialization recursively or just for all keys
        for k, v in d.items():
            if isinstance(v, (date, datetime)):
                d[k] = str(v)
        safe_weekly_data.append(d)
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request, 
        "page_title": project.name, 
        "project": project,
        "weekly_data": safe_weekly_data,
        # New Context
        "gantt": {
            "view_mode": view_mode,
            "focus_date": f_date,
            "next_date": (f_date + timedelta(days=30)).isoformat(), # Rough jump, frontend can do better logic
            "prev_date": (f_date - timedelta(days=30)).isoformat(),
            "headers": timeline['headers'],
            "grid_template": timeline['grid_template'],
            "bars": final_bars
        }
    })

@app.get("/projects/{project_id}/planning", response_class=HTMLResponse)
async def project_planning(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
         return HTMLResponse("Project not found", status_code=404)
    
    weekly_data = db.query(models.WeeklyProgress).filter(models.WeeklyProgress.project_id == project_id).order_by(models.WeeklyProgress.week_number).all()
    
    # Serialize safely
    safe_weekly_data = []
    for w in weekly_data:
        d = w.__dict__.copy()
        if "_sa_instance_state" in d:
            del d["_sa_instance_state"]
        for k, v in d.items():
            if isinstance(v, (date, datetime)):
                d[k] = str(v)
        safe_weekly_data.append(d)

    return templates.TemplateResponse("project_planning.html", {
        "request": request,
        "page_title": f"Plan: {project.name}",
        "project": project,
        "weekly_data": safe_weekly_data
    })

@app.get("/workload", response_class=HTMLResponse)
async def workload(request: Request):
    return templates.TemplateResponse("workload.html", {"request": request, "page_title": "Engineer Workload"})
