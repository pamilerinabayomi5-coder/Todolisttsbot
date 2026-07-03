import asyncio
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application
import database
from config import logger

async def reminder_worker(app: Application):
    logger.info("Background reminder scheduler started.")
    while True:
        try:
            now_utc = datetime.utcnow()
            tasks = database.get_all_pending_reminders()
            
            for t in tasks:
                user_id = t['user_id']
                settings = database.get_user_settings(user_id)
                tz_str = settings['timezone'] if settings else 'UTC'
                
                try:
                    tz = pytz.timezone(tz_str)
                except Exception:
                    tz = pytz.utc
                
                try:
                    rem_dt_naive = datetime.strptime(f"{t['due_date']} {t['reminder_time']}", "%Y-%m-%d %H:%M")
                    rem_dt_loc = tz.localize(rem_dt_naive)
                    rem_dt_utc = rem_dt_loc.astimezone(pytz.utc).replace(tzinfo=None)
                except Exception as ex:
                    logger.error(f"Error parsing date for task {t['id']}: {ex}")
                    continue

                if rem_dt_utc <= now_utc:
                    if settings and settings['notification_pref'] == 'enabled':
                        msg = (
                            f"⏰ *TASK REMINDER*\n\n"
                            f"📌 *{t['title']}*\n"
                            f"📝 {t['description'] or 'No description'}\n\n"
                            f"📁 Category: {t['category']} | 🚨 Priority: {t['priority']}"
                        )
                        try:
                            await app.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                            logger.info(f"Notification sent to user {user_id} for task {t['id']}")
                        except Exception as e:
                            logger.error(f"Failed to send telegram message to {user_id}: {e}")
                    
                    # Manage Recurrence
                    recur = t['recurrence']
                    if recur == 'Daily':
                        next_date = (rem_dt_naive + timedelta(days=1)).strftime("%Y-%m-%d")
                        database.update_task_field(t['id'], 'due_date', next_date)
                    elif recur == 'Weekly':
                        next_date = (rem_dt_naive + timedelta(weeks=1)).strftime("%Y-%m-%d")
                        database.update_task_field(t['id'], 'due_date', next_date)
                    elif recur == 'Monthly':
                        next_date = (rem_dt_naive + timedelta(days=30)).strftime("%Y-%m-%d")
                        database.update_task_field(t['id'], 'due_date', next_date)
                    else:
                        database.update_task_status(t['id'], 'Completed')
                        
        except Exception as e:
            logger.error(f"Error within reminder worker cycle: {e}", exc_info=True)
            
        await asyncio.sleep(45)
