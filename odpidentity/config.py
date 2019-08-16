import os


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SERVER_NAME = os.getenv('FLASK_SERVER_NAME')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = os.getenv('DATABASE_ECHO', '').lower() == 'true'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HYDRA_ADMIN_URL = os.getenv('HYDRA_ADMIN_URL')
    HYDRA_PUBLIC_URL = os.getenv('HYDRA_PUBLIC_URL')
    HYDRA_CLIENT_ID = os.getenv('HYDRA_CLIENT_ID')
    HYDRA_CLIENT_SECRET = os.getenv('HYDRA_CLIENT_SECRET')
    HYDRA_SCOPES = os.getenv('HYDRA_SCOPES', '').split()
