from odp.config import config
from odp.lib.media import MediaRepoClient


def get_media_repo_client() -> MediaRepoClient:
    """
    MediaRepo API dependency
    """
    return MediaRepoClient(
        media_repo_url=config.MEDIA.REPOSITORY_BASE_URL,
        username=config.MEDIA.USERNAME,
        password=config.MEDIA.PASSWORD
    )
