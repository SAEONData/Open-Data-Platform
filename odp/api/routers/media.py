from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from odp.lib.media import MediaRepoClient
from odp.lib.exceptions import MediaRepositoryError
from odp.api.dependencies.media import get_media_repo_client

router = APIRouter()


@router.get('/{file_path:path}')
async def get_media_download(
        file_path: str,
        media_repo_client: MediaRepoClient = Depends(get_media_repo_client),
):
    try:
        download_link = media_repo_client.get_download_link(file_path)
        return RedirectResponse(download_link)
    except MediaRepositoryError as e:
        raise HTTPException(e.status_code, e.error_detail) from e
