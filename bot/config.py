import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UON_TOKEN = os.getenv("UON_TOKEN")
UON_BASE_URL = os.getenv("UON_BASE_URL")
MANAGER_LINK = os.getenv("MANAGER_LINK")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1000000000000"))
