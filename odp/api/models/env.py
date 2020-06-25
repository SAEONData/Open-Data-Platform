from enum import Enum


class ServerEnv(str, Enum):
    development = 'development'
    testing = 'testing'
    staging = 'staging'
    production = 'production'
