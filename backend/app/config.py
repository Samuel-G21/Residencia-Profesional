import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER', 'pemex_user')}:{os.getenv('DB_PASSWORD', 'pemex_password')}@{os.getenv('DB_HOST', 'db')}/{os.getenv('DB_NAME', 'pemex_db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOTENBERG_URL = os.getenv('GOTENBERG_URL', 'http://gotenberg:3000')
