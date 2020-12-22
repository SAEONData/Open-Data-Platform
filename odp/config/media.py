from pydantic import AnyHttpUrl

from odp.config import BaseConfig


class MediaConfig(BaseConfig):
    class Config:
        env_prefix = 'MEDIA_'

    # base URL for media repository (to which download links resolve)
    REPOSITORY_BASE_URL: AnyHttpUrl
    USERNAME: str    # Media repository username
    PASSWORD: str    # Media repository password
