import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers
import scheduler
from config import BOT_TOKEN, logger

def main():
    # Database Initialization
    database.init_db()

    # Application Setup
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation Handlers
    add_task_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.init_add_task, pattern="^menu_add$")],
        states={
            handlers.ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.add_title_rcv)],
            handlers.ADD_DESC: [CommandHandler("skip", handlers.skip_desc), MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.add_desc_rcv)],
            handlers.ADD_CAT: [CallbackQueryHandler(handlers.add_cat_rcv, pattern="^cat_")],
            handlers.ADD_PRIO: [CallbackQueryHandler(handlers.add_prio_rcv, pattern="^prio_")],
            handlers.ADD_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.add_date_rcv)],
            handlers.ADD_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.add_time_rcv)],
            handlers.ADD_RECUR: [CallbackQueryHandler(handlers.add_recur_rcv, pattern="^recur_")]
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_conv), CallbackQueryHandler(handlers.cancel_conv, pattern="^menu_main$")],
        per_message=False
    )

    view_task_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.show_tasks_menu, pattern="^menu_tasks$")],
        states={
            handlers.EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.select_task_inline_routing)]
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_conv), CallbackQueryHandler(handlers.cancel_conv, pattern="^menu_main$")],
        per_message=False
    )

    tz_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.init_tz_change, pattern="^sett_tz$")],
        states={
            handlers.SET_TZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.rx_tz)]
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_conv)]
    )

    csv_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.init_csv_import, pattern="^sett_import$")],
        states={
            handlers.IMP_CSV: [MessageHandler(filters.Document.ALL, handlers.rx_csv)]
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_conv)]
    )

    # Base Handlers Registration
    app.add_handler(CommandHandler("start", handlers.start_cmd))
    app.add_handler(CommandHandler("cancel", handlers.cancel_conv))
    app.add_handler(CommandHandler("search", handlers.search_cmd))
    
    app.add_handler(add_task_conv)
    app.add_handler(view_task_conv)
    app.add_handler(tz_conv)
    app.add_handler(csv_conv)
    
    app.add_handler(CallbackQueryHandler(handlers.dispatch_menu_routing))

    # Background Tasks Initialization
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler.reminder_worker(app))

    logger.info("Bot execution loop initialized successfully.")
    app.run_polling()

if __name__ == "__main__":
    main()
