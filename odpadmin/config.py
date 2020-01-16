import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SERVER_NAME = os.getenv('FLASK_SERVER_NAME')
    FLASK_ADMIN_SWATCH = os.getenv('FLASK_ADMIN_SWATCH')

    HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')
    HYDRA_PUBLIC_URL = os.getenv('HYDRA_PUBLIC_URL')
    OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
    OAUTH2_CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')
    OAUTH2_SCOPES = os.getenv('OAUTH2_SCOPES', '').split()

    ADMIN_INSTITUTION = os.getenv('ADMIN_INSTITUTION')
    ADMIN_ROLE = os.getenv('ADMIN_ROLE')
    ADMIN_SCOPE = os.getenv('ADMIN_SCOPE')
