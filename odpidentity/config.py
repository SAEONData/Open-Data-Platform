import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SERVER_NAME = os.getenv('FLASK_SERVER_NAME')

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '25'))

    HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')
    HYDRA_LOGIN_EXPIRY = int(os.getenv('HYDRA_LOGIN_EXPIRY', '86400'))

    HYDRA_PUBLIC_URL = os.getenv('HYDRA_PUBLIC_URL')
    OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
    OAUTH2_CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')
    OAUTH2_SCOPES = os.getenv('OAUTH2_SCOPES', '').split()

    PASSWORD_COMPLEXITY_DESCRIPTION = os.getenv('PASSWORD_COMPLEXITY_DESCRIPTION')
