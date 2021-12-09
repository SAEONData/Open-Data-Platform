from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def get_status():
    """API health check."""
    return "OK"
