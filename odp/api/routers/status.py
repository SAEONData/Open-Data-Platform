from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def get_status():
    """Check whether the API is alive."""
    return "OK"
