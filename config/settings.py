import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

    @staticmethod
    def validate():
        if not Config.GOOGLE_CREDENTIALS_PATH:
            print("WARNING: GOOGLE_CREDENTIALS_PATH has not been configured in the .env file.")