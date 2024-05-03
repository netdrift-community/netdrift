from fastapi import APIRouter

from netdrift.api.intent import full as intent_full
from netdrift.api.intent import group as intent_group
from netdrift.api.intent import partial as intent_partial

api_router = APIRouter()

api_router.include_router(intent_full.router, prefix="/intent/full")
api_router.include_router(intent_group.router, prefix="/intent/group")
api_router.include_router(intent_partial.router, prefix="/intent/partial")
