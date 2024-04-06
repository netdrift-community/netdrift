from fastapi import APIRouter

api_router = APIRouter()

from netdrift.api import intent, jobs

api_router.include_router(intent.router, prefix="/intent")
api_router.include_router(jobs.router, prefix="/jobs")
