import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TodoListTSBot")

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME", "todolist.db")
DEFAULT_TZ = os.getenv("TIMEZONE", "UTC")

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN environment variable is missing!")
    sys.exit("Error: BOT_TOKEN is required to run the bot.")
