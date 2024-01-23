import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
ADMINS_IDS = os.getenv('ADMINS_IDS').split(', ')
ADMINS_IDS = [int(i) for i in ADMINS_IDS]
