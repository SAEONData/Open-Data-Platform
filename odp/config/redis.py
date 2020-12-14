from odp.config import BaseConfig


class RedisConfig(BaseConfig):
    class Config:
        env_prefix = 'REDIS_'

    HOST: str = 'localhost'
    PORT: int = 6379
    DB: int = 0
