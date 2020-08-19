import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('ADMIN_FLASK_KEY')
    FLASK_ADMIN_SWATCH = os.getenv('FLASK_ADMIN_SWATCH')

    DATABASE_URL = os.getenv('DATABASE_URL')
    HYDRA_PUBLIC_URL = os.getenv('HYDRA_PUBLIC_URL')
    OAUTH2_CLIENT_ID = os.getenv('ADMIN_OAUTH2_ID')
    OAUTH2_CLIENT_SECRET = os.getenv('ADMIN_OAUTH2_SECRET')
    OAUTH2_SCOPES = os.getenv('ADMIN_OAUTH2_SCOPES', '').split()

    ADMIN_INSTITUTION = os.getenv('ADMIN_INSTITUTION')
    ADMIN_ROLE = os.getenv('ADMIN_ROLE')
    ADMIN_SCOPE = os.getenv('ADMIN_SCOPE')
