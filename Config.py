import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger("Config")

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    logger.warning("API_ID or API_HASH is missing! Bot will not start correctly.")

try:
    API_ID = int(API_ID)
except (TypeError, ValueError):
    logger.warning("API_ID should be an integer.")

# Optional Variables
BIO_MESSAGE = os.getenv("BIO")

# SUDO Users
sudo_env = os.getenv("SUDO", "")
SUDO = []
if sudo_env:
    try:
        SUDO = list(map(int, sudo_env.split()))
    except ValueError:
        logger.warning("SUDO environment variable contains invalid user IDs.")

# Dynamic Session Loading
# Automatically finds any environment variable starting with STRING or SESSION
session_vars = []
for key, value in os.environ.items():
    if (key.startswith("STRING") or key.startswith("SESSION")) and value:
        session_vars.append((key, value))

# Sort by key to ensure consistent order (STRING1, STRING2, ...)
session_vars.sort(key=lambda x: x[0])

SESSIONS = [value for key, value in session_vars]

if not SESSIONS:
    logger.warning("No session strings found! Set STRING1, STRING2, etc. in environment variables.")
