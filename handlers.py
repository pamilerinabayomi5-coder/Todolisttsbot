import csv
import io
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import keyboards
import utils
from config import logger

# Conversation State Consts
ADD_TITLE, ADD_DESC, ADD_CAT, ADD_PRIO, ADD_DATE, ADD_TIME, ADD_RECUR = range(7)
EDIT_TITLE, EDIT_REM_DATE, EDIT_REM_TIME = range(7, 10)
SET_TZ, IMP_CSV = range(10, 12)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.add_user(user.id, user.username, user.first_name)
    msg = (
        f"👋 Hello, *{utils.escape_markdown(user.first_name)}*!\n\n"
        f"Welcome to *TodoListTSBot* 📋\n"
        f"Efficiently orchestrate your day, map schedules, and receive persistent updates.\n\n"
        f"Use the navigation layout below to begin."
    )
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboards.main_menu_keyboard())

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.user_data.clear()
    msg = "❌ Operation cancelled. Back to safety."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg, reply_markup=keyboards.back_to_main_keyboard())
    elif update.message:
        await update.message.reply_text(msg, reply_markup=keyboards.back_to_main_keyboard())
    return ConversationHandler.END

# --- ADD TASK CONVERSATION ---
async def init_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✏️ Enter the *Title* for your new task:")
    return ADD_TITLE

async def add_title_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("📝 Enter a short *Description* (or type /skip to bypass):")
    return ADD_DESC

async def skip_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['desc'] = ""
    await update.message.reply_text("📁 Select a structural category:", reply_markup=keyboards.categories_keyboard())
    return ADD_CAT

async def add_desc_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['desc'] = update.message.text
    await update.message.reply_text("📁 Select a structural category:", reply_markup=keyboards.categories_keyboard())
    return ADD_CAT

async def add_cat_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['cat'] = query.data.split('_')[1]
    await query.edit_message_text("🚨 Assign relative workflow priority:", reply_markup=keyboards.priority_keyboard())
    return ADD_PRIO

async def add_prio_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['prio'] = query.data.split('_')[1]
    await query.edit_message_text("📅 Enter due date in exact format `YYYY-MM-DD` (e.g., 2026-12-31):")
    return ADD_DATE

async def add_date_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not utils.validate_date(txt):
        await update.message.reply_text("⚠️ Invalid Format. Please output validation conforming string `YYYY-MM-DD`:")
        return ADD_DATE
    context.user_data['date'] = txt
    await update.message.reply_text("⏰ Enter alert runtime confirmation timestamp matching format `HH:MM` (24hr limit):")
    return ADD_TIME

async def add_time_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if not utils.validate_time(txt):
        await update.message.reply_text("⚠️ Invalid Format. Standardize target clock matching `HH:MM`:")
        return ADD_TIME
    context.user_data['time'] = txt
    await update.message.reply_text("🔁 Choose recurrence type:", reply_markup=keyboards.recurrence_keyboard())
    return ADD_RECUR

async def add_recur_rcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    recur = query.data.split('_')[1]
    
    uid = update.effective_user.id
    ud = context.user_data
    
    database.add_task(uid, ud['title'], ud['desc'], ud['cat'], ud['prio'], ud['date'], ud['time'], recur)
    await query.edit_message_text("🎉 Task generated and scheduled securely!", reply_markup=keyboards.back_to_main_keyboard())
    await context.user_data.clear()
    return ConversationHandler.END

# --- MY TASKS & ACTIONS ---
async def show_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    tasks = database.get_tasks(uid)
    
    if not tasks:
        await query.edit_message_text("📭 Work allocation empty! Try adding new targets.", reply_markup=keyboards.back_to_main_keyboard())
        return

    msg = "📋 *Active Context Portfolio Matrix:*\n\n"
    for t in tasks:
        status_icon = "✅" if t['status'] == "Completed" else "⏳"
        msg += f"{status_icon} *[{t['id']}] {t['title']}*\n📅 Due: {t['due_date']} {t['reminder_time']} | 🚨 {t['priority']}\n\n"
    
    msg += "💡 _To modify a specific item context, send its exact integer ID identifier directly below:_ (Or use /cancel to escape)"
    await query.edit_message_text(msg, parse_mode="Markdown")
    return EDIT_TITLE  # Routing inside a general listener

async def select_task_inline_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if not val.isdigit():
        await update.message.reply_text("⚠️ Numerical input needed. Provide a proper instance ID:")
        return EDIT_TITLE
    
    task = database.get_task_by_id(int(val))
    if not task or task['user_id'] != update.effective_user.id:
        await update.message.reply_text("❌ Element references no accessible entity records. Re-enter identifier:")
        return EDIT_TITLE
    
    msg = (
        f"📊 *Target Identity Mapping:* #{task['id']}\n\n"
        f"📌 *Title:* {task['title']}\n"
        f"📝 *Description:* {task['description'] or 'Empty'}\n"
        f"📁 *Category:* {task['category']} | 🚨 *Priority:* {task['priority']}\n"
        f"📅 *Deadline:* {task['due_date']} {task['reminder_time']}\n"
        f"🔁 *Type:* {task['recurrence']}\n"
        f"⚡ *State:* {task['status']}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboards.task_action_keyboard(task['id']))
    return ConversationHandler.END

# --- STATIC INLINE DISPATCHERS ---
async def dispatch_menu_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "menu_main":
        await query.edit_message_text("🔮 Root interface dashboard operational:", reply_markup=keyboards.main_menu_keyboard())
    elif data == "menu_stats":
        tasks = database.get_tasks(update.effective_user.id)
        tot, comp, pend, ov, pct = utils.calculate_stats(tasks)
        msg = (
            f"📊 *Workflow Metrics Evaluation Summary*\n\n"
            f"🔢 Total Submissions: {tot}\n"
            f"✅ Realized Closures: {comp}\n"
            f"⏳ Outstanding Items: {pend}\n"
            f"⚠️ Overdue Windows: {ov}\n"
            f"📈 Success Quotient: {pct:.1f}%"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    elif data == "menu_settings":
        await query.edit_message_text("⚙️ *Local system state customization parameters:*", parse_mode="Markdown", reply_markup=keyboards.settings_keyboard())
    elif data == "menu_help":
        msg = (
            "❓ *Usage Protocol & Operation Documentation*\n\n"
            "➕ *Add Tasks:* Follow standard procedural workflows via prompts.\n"
            "⏰ *Notification Pipeline:* Runs engine processes every 45 seconds for deadlines.\n"
            "📥 *Migration Engine:* Standardized parsing structures allow dynamic adjustments.\n"
            "❌ *Cancel Operation:* Use `/cancel` command anytime."
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    elif data == "menu_about":
        msg = "ℹ️ *System Spec:* TodoListTSBot v2.0.0-Stable\nEngine Framework: Python 3.12/PTB v21\n\n🛡️ _Privacy Assurance Statement: Data isolates user states utilizing embedded engine protocols._"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    elif data == "sett_notif":
        uid = update.effective_user.id
        sett = database.get_user_settings(uid)
        nxt = "disabled" if sett['notification_pref'] == "enabled" else "enabled"
        database.update_user_settings(uid, "notification_pref", nxt)
        await query.edit_message_text(f"🔔 Notification pipeline explicitly shifted to *{nxt.upper()}*.", parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    elif data == "sett_export":
        tasks = database.get_tasks(update.effective_user.id)
        bio = utils.export_tasks_to_csv(tasks)
        await context.bot.send_document(chat_id=update.effective_user.id, document=bio, filename="tasks.csv", caption="📥 Local storage operational dataset export successful.")
    elif data.startswith("task_done_"):
        tid = int(data.split('_')[2])
        database.update_task_status(tid, "Completed")
        await query.edit_message_text("✅ Target entity updated to matching terminal status: *Completed*", parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    elif data.startswith("task_del_"):
        tid = int(data.split('_')[2])
        database.delete_task(tid)
        await query.edit_message_text("🗑️ Task permanently dropped from active ledger indexes.", reply_markup=keyboards.back_to_main_keyboard())

# --- CONVERSATIONAL SETTING UPDATES ---
async def init_tz_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🌐 Output string representations identifier matching valid `pytz` instance (e.g., `America/New_York`, `Europe/London`, `Asia/Kolkata`):")
    return SET_TZ

async def rx_tz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    import pytz
    if txt not in pytz.all_timezones:
        await update.message.reply_text("⚠️ Unrecognized zone identity marker string. Review exact reference and re-enter:")
        return SET_TZ
    database.update_user_settings(update.effective_user.id, "timezone", txt)
    await update.message.reply_text(f"✅ Runtime localization parameter customized to: `{txt}`", parse_mode="Markdown", reply_markup=keyboards.back_to_main_keyboard())
    return ConversationHandler.END

async def init_csv_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("📤 Upload your structured `.csv` asset schema layout mapping now:")
    return IMP_CSV

async def rx_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith('.csv'):
        await update.message.reply_text("⚠️ File type rejection exception mismatch. Please supply standard functional `.csv` file:")
        return IMP_CSV
    
    file_bytes = await context.bot.get_file(doc.file_id)
    content = await file_bytes.download_as_bytearray()
    
    try:
        stream = io.StringIO(content.decode('utf-8'))
        reader = csv.reader(stream)
        next(reader) # Skip headers safely
        
        counter = 0
        for row in reader:
            if len(row) >= 8:
                database.add_task(update.effective_user.id, row[1], row[2], row[3], row[4], row[6], row[7], row[8] if len(row)>8 else 'None')
                counter += 1
        await update.message.reply_text(f"🚀 Data import complete. Merged {counter} new tasks into database successfully.", reply_markup=keyboards.back_to_main_keyboard())
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        await update.message.reply_text("❌ System tracking fatal collision failure unpacking metrics sequence structure validation checks.", reply_markup=keyboards.back_to_main_keyboard())
    
    return ConversationHandler.END

# --- SEARCH FUNCTIONALITY ---
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a search query. Usage: `/search keyword`")
        return
    query_str = " ".join(context.args)
    results = database.search_tasks_db(update.effective_user.id, query_str)
    if not results:
        await update.message.reply_text("🔍 No matching tasks found.")
        return
    
    msg = f"🔍 *Search results for '{utils.escape_markdown(query_str)}':*\n\n"
    for t in results:
        status_icon = "✅" if t['status'] == "Completed" else "⏳"
        msg += f"{status_icon} *[{t['id']}] {t['title']}* ({t['status']})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")
