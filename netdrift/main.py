from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from netdrift.dependencies import get_api_key
from netdrift import api, exceptions

app = FastAPI(dependencies=[Depends(get_api_key)])


@app.exception_handler(exceptions.NetdriftBaseException)
async def netdrift_exception_handler(
    request: Request, exc: exceptions.NetdriftBaseException
):
    return JSONResponse(exc.json(), exc.status)


@app.exception_handler(NotImplementedError)
async def netdrift_not_implemented_handler(request: Request, exc: NotImplementedError):
    raise exceptions.NetdriftNotImplementedError


app.include_router(api.api_router, prefix="/v1")
