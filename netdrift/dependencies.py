from typing import Annotated

from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from netdrift.config import settings

API_KEY_HEADER = APIKeyHeader(name=settings.API_TOKEN_KEY, auto_error=False)


def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> None:
    """Basic API key authentication.

    Args:
        api_key_header:     API Key header name to search in HTTP headers.
    """
    if api_key_header != settings.API_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return


async def db() -> AsyncIOMotorDatabase:
    """Basic Database dependency for FastAPI implementation.

    Args:
        uri:        MongoDB URI
        db:         Name of database in MongoDB
    """
    client = AsyncIOMotorClient(str(settings.MONGO_URI), serverSelectionTimeoutMS=3000)
    database = client[settings.MONGO_DB]
    return database


DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(db)]
