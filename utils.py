import csv
import io
import html
from datetime import datetime
import pytz
from config import logger

def escape_markdown(text: str) -> str:
    if not text:
        return ""
    # Returns safe strings for HTML parsing inside telegram messages
    return html.escape(text)

def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def calculate_stats(tasks):
    total = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == 'Completed')
    pending = sum(1 for t in tasks if t['status'] == 'Pending')
    overdue = 0
    
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    for t in tasks:
        if t['status'] == 'Pending' and t['due_date'] and t['reminder_time']:
            t_dt = f"{t['due_date']} {t['reminder_time']}"
            if t_dt < now_str:
                overdue += 1

    pct = (completed / total * 100) if total > 0 else 0.0
    return total, completed, pending, overdue, pct

def export_tasks_to_csv(tasks) -> io.BytesIO:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Description", "Category", "Priority", "Status", "Due Date", "Reminder Time", "Recurrence"])
    for t in tasks:
        writer.writerow([t['id'], t['title'], t['description'], t['category'], t['priority'], t['status'], t['due_date'], t['reminder_time'], t['recurrence']])
    
    bio = io.BytesIO(output.getvalue().encode('utf-8'))
    bio.name = "tasks_export.csv"
    return bio
