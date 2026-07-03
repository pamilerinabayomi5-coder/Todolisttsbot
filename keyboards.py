from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("➕ Add Task", callback_data="menu_add"), InlineKeyboardButton("📋 My Tasks", callback_data="menu_tasks")],
        [InlineKeyboardButton("⏰ Reminders", callback_data="menu_reminders"), InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")],
        [InlineKeyboardButton("⚙ Settings", callback_data="menu_settings"), InlineKeyboardButton("❓ Help", callback_data="menu_help")],
        [InlineKeyboardButton("ℹ About", callback_data="menu_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_main_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")]])

def categories_keyboard():
    keyboard = [
        [InlineKeyboardButton("Work", callback_data="cat_Work"), InlineKeyboardButton("Personal", callback_data="cat_Personal")],
        [InlineKeyboardButton("Study", callback_data="cat_Study"), InlineKeyboardButton("Shopping", callback_data="cat_Shopping")],
        [InlineKeyboardButton("Custom/Other", callback_data="cat_Custom")]
    ]
    return InlineKeyboardMarkup(keyboard)

def priority_keyboard():
    keyboard = [
        [InlineKeyboardButton("🟢 Low", callback_data="prio_Low"),
         InlineKeyboardButton("🟡 Medium", callback_data="prio_Medium"),
         InlineKeyboardButton("🔴 High", callback_data="prio_High")]
    ]
    return InlineKeyboardMarkup(keyboard)

def recurrence_keyboard():
    keyboard = [
        [InlineKeyboardButton("None", callback_data="recur_None"), InlineKeyboardButton("Daily", callback_data="recur_Daily")],
        [InlineKeyboardButton("Weekly", callback_data="recur_Weekly"), InlineKeyboardButton("Monthly", callback_data="recur_Monthly")]
    ]
    return InlineKeyboardMarkup(keyboard)

def task_action_keyboard(task_id: int):
    keyboard = [
        [InlineKeyboardButton("✅ Complete", callback_data=f"task_done_{task_id}"),
         InlineKeyboardButton("✏ Edit Title", callback_data=f"task_edit_{task_id}")],
        [InlineKeyboardButton("🔔 Edit Reminder", callback_data=f"task_rem_{task_id}"),
         InlineKeyboardButton("🗑 Delete", callback_data=f"task_del_{task_id}")],
        [InlineKeyboardButton("🔙 Back to List", callback_data="menu_tasks")]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌐 Change Timezone", callback_data="sett_tz")],
        [InlineKeyboardButton("🔔 Notifications Toggle", callback_data="sett_notif")],
        [InlineKeyboardButton("📥 Export Tasks (CSV)", callback_data="sett_export")],
        [InlineKeyboardButton("📤 Import Tasks (CSV)", callback_data="sett_import")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
