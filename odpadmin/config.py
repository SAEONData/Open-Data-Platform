import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SERVER_NAME = os.getenv('FLASK_SERVER_NAME')
    FLASK_ADMIN_SWATCH = os.getenv('FLASK_ADMIN_SWATCH')

    HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')
    HYDRA_PUBLIC_URL = os.getenv('HYDRA_PUBLIC_URL')
    HYDRA_CLIENT_ID = os.getenv('HYDRA_CLIENT_ID')
    HYDRA_CLIENT_SECRET = os.getenv('HYDRA_CLIENT_SECRET')
    HYDRA_SCOPES = os.getenv('HYDRA_SCOPES', '').split()

    ADMIN_INSTITUTION = os.getenv('ADMIN_INSTITUTION')
    ADMIN_ROLE = os.getenv('ADMIN_ROLE')
    ADMIN_SCOPE = os.getenv('ADMIN_SCOPE')
