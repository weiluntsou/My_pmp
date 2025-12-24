from datetime import date, timedelta
import math

def get_iso_week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())

def calculate_timeline(view_mode: str, focus_date: date):
    """
    Calculates timeline boundaries and headers.
    """
    headers = []
    
    if view_mode == 'week':
        # Start from Monday of focus_date
        start_date = get_iso_week_start(focus_date)
        total_units = 12
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i in range(total_units):
            current = start_date + timedelta(weeks=i)
            # Label: "W12 (Mar 20)" or just week num? User wants "2026年 1月" range indicated globally.
            # Headers could be "W{iso} {MonDD}"
            iso_week = current.isocalendar()[1]
            label = f"W{iso_week} ({current.month}/{current.day})"
            headers.append({
                "label": label, 
                "start": current, 
                "end": current + timedelta(days=6)
            })
            
        end_date = start_date + timedelta(weeks=total_units) - timedelta(days=1)
        grid_template = f"repeat({total_units}, 1fr)"
        
    elif view_mode == 'month':
        # Start from 1st of current month
        start_date = date(focus_date.year, focus_date.month, 1)
        total_units = 12
        
        curr = start_date
        for i in range(total_units):
            label = curr.strftime("%Y-%m") # 2025-12
            # Find end of month
            if curr.month == 12:
                next_month = date(curr.year + 1, 1, 1)
            else:
                next_month = date(curr.year, curr.month + 1, 1)
                
            headers.append({
                "label": label,
                "start": curr,
                "end": next_month - timedelta(days=1)
            })
            curr = next_month
            
        end_date = curr - timedelta(days=1)
        grid_template = f"repeat({total_units}, 1fr)"

    elif view_mode == 'quarter':
        # Start from 1st of current quarter
        q_month = ((focus_date.month - 1) // 3) * 3 + 1
        start_date = date(focus_date.year, q_month, 1)
        total_units = 8 # 2 years
        
        curr = start_date
        for i in range(total_units):
            q_num = ((curr.month - 1) // 3) + 1
            label = f"{curr.year} Q{q_num}"
            
            # Add 3 months
            # simple trick: year + (month+3-1)//12, (month+3-1)%12 + 1
            # logic: add 3 months
            y, m = curr.year, curr.month
            tgt_m = m + 3
            tgt_y = y + (tgt_m - 1) // 12
            tgt_m = (tgt_m - 1) % 12 + 1
            next_q = date(tgt_y, tgt_m, 1)
            
            headers.append({
                "label": label,
                "start": curr,
                "end": next_q - timedelta(days=1)
            })
            curr = next_q
            
        end_date = curr - timedelta(days=1)
        grid_template = f"repeat({total_units}, 1fr)"
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "headers": headers,
        "grid_template": grid_template,
        "total_units": total_units
    }

def calculate_grid_position(task_start: date, task_end: date, timeline_start: date, view_mode: str):
    """
    Returns grid_column_start and grid_column_span (1-based index).
    """
    if not task_start or not task_end:
        return None
        
    start_index = 0
    end_index = 0
    
    if view_mode == 'week':
        # Diff in weeks
        # Round down to start of week
        tl_iso = get_iso_week_start(timeline_start)
        task_iso = get_iso_week_start(task_start)
        
        diff_days = (task_iso - tl_iso).days
        start_index = int(diff_days / 7) + 1 # 1-based
        
        # Duration
        # task_end might be mid-week, so we encompass that week
        task_end_iso = get_iso_week_start(task_end)
        end_diff = (task_end_iso - tl_iso).days
        end_index = int(end_diff / 7) + 1
        
        span = end_index - start_index + 1
        
    elif view_mode == 'month':
        # Diff in months
        diff_years = task_start.year - timeline_start.year
        diff_months = task_start.month - timeline_start.month
        start_index = (diff_years * 12 + diff_months) + 1
        
        diff_years_end = task_end.year - timeline_start.year
        diff_months_end = task_end.month - timeline_start.month
        end_index = (diff_years_end * 12 + diff_months_end) + 1
        
        span = end_index - start_index + 1
        
    elif view_mode == 'quarter':
        # Diff in quarters
        def get_q(d): return (d.year * 4) + ((d.month - 1) // 3)
        
        q_start = get_q(timeline_start)
        q_task = get_q(task_start)
        start_index = (q_task - q_start) + 1
        
        q_end = get_q(task_end)
        end_index = (q_end - q_start) + 1
        
        span = end_index - start_index + 1

    return start_index, span
