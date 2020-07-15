from enum import Enum


class ServerEnv(str, Enum):
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    STAGING = 'staging'
    PRODUCTION = 'production'
