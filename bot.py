import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Load environment variables (for local testing; Render uses its Environment settings)
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("TodoListTSBot")

# Define Conversation States
ADD_TASK, VIEW_TASK, SET_TZ, EXPORT_CSV = range(4)

# --- 1. DATABASE INITIALIZATION ---
# A tiny placeholder simulating your log: "Database initialized successfully."
def init_db():
    logger.info("Database initialized successfully.")

# --- 2. HANDLER FUNCTIONS ---

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! Welcome to your Todo List Bot.\n\n"
        "Available commands:\n"
        "/add - Add a new task\n"
        "/view - View your tasks\n"
        "/timezone - Set your timezone\n"
        "/export - Export tasks to CSV\n"
        "/cancel - Cancel current operation"
    )

# /cancel fallback command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Action canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Add Task Logic ---
async def start_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please enter the title of the task you want to add:")
    return ADD_TASK

async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_title = update.message.text
    # Insert saving logic/database call here
    await update.message.reply_text(f"✓ Task '{task_title}' added successfully!")
    return ConversationHandler.END

# --- View Task Logic ---
async def start_view_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Insert database pulling logic here
    await update.message.reply_text("Here are your active tasks:\n1. Complete deployment on Render 🚀")
    return ConversationHandler.END

# --- Timezone Logic ---
async def start_tz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please enter your preferred timezone (e.g., UTC, America/New_York):")
    return SET_TZ

async def save_tz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tz = update.message.text
    await update.message.reply_text(f"✓ Timezone updated to: {tz}")
    return ConversationHandler.END

# --- CSV Export Logic ---
async def start_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Generating your CSV export...")
    # Insert CSV generating code here
    await update.message.reply_text("Feature ready! (Simulated CSV download)")
    return ConversationHandler.END


# --- 3. CONVERSATION HANDLER DEFINITIONS ---
# Defined OUTSIDE and BEFORE main() so they are globally initialized when main() calls them.

# Fixes the PTBUserWarning by explicitly setting per_message=True or tracking appropriately
add_task_conv = ConversationHandler(
    entry_points=[CommandHandler("add", start_add_task)],
    states={
        ADD_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_task)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True 
)

view_task_conv = ConversationHandler(
    entry_points=[CommandHandler("view", start_view_task)],
    states={
        VIEW_TASK: []
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True
)

tz_conv = ConversationHandler(
    entry_points=[CommandHandler("timezone", start_tz)],
    states={
        SET_TZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_tz)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True
)

csv_conv = ConversationHandler(
    entry_points=[CommandHandler("export", start_csv)],
    states={
        EXPORT_CSV: []
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True
)


# --- 4. MAIN APPLICATION ---
def main() -> None:
    # 1. Start setup routines
    init_db()

    # 2. Extract Token from environment variables
    # Be sure to add TELEGRAM_TOKEN in Render's "Environment Variables" settings tab!
    TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_FALLBACK_TOKEN_IF_LOCAL")

    # 3. Build application framework (Handles loop setup automatically)
    application = ApplicationBuilder().token(TOKEN).build()

    # 4. Register structural conversation handlers (defined cleanly above)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_task_conv)
    application.add_handler(view_task_conv)
    application.add_handler(tz_conv)
    application.add_handler(csv_conv)

    # 5. Ignite Polling Engine (This cleans up and runs the async loop under the hood)
    logger.info("Starting bot polling system...")
    application.run_polling()

if __name__ == '__main__':
    main()
