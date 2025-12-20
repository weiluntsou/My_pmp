from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.routers import projects, meetings, sync, reports
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
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
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
        safe_weekly_data.append(d)
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request, 
        "page_title": project.name, 
        "project": project,
        "weekly_data": safe_weekly_data
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
