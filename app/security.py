from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Неверный API ключ")
