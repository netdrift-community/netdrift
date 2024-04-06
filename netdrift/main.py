from fastapi import FastAPI, Depends

from netdrift.dependencies import get_api_key
from netdrift import api

app = FastAPI(dependencies=[Depends(get_api_key)])

app.include_router(api.api_router, prefix="/v1")


@app.get("/")
async def home():
    return {}
