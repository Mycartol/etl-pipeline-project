from dotenv import load_dotenv
import os

load_dotenv()

USE_OPENAI   = os.getenv("USE_OPENAI", "true").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")