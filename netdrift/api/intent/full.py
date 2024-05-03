from fastapi import APIRouter, Depends

from netdrift.dependencies import DatabaseDep
from netdrift.models.mongo import PyObjectId
from netdrift.models.intent import (
    FullIntentConfigQuery,
    FullIntentConfigRead,
    FullIntentConfigCreate,
    FullIntentConfigUpdate,
)
from netdrift import crud, exceptions, logic


router = APIRouter()


@router.get("/", response_model=list[FullIntentConfigRead])
async def get_all_full_intent(
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
    params: FullIntentConfigQuery = Depends(),
):
    """Get all full intents.

    Args:
        db:     AsyncIOMotorDatabase object.
        skip:   Offset when searching the database.
        limit:  Limit database resources returned.
        params: Query params.
    """
    param_query = params.build_query()
    intents = await crud.full_intent.get_multi(db, skip, limit, param_query)
    return intents


@router.get("/{intent_id}", response_model=FullIntentConfigRead)
async def get_full_intent(
    db: DatabaseDep,
    intent_id: PyObjectId,
):
    """Get a specific full intent.

    Args:
        db:             AsyncIOMotorDatabase object.
        intent_id:      Intent Id.
    """
    if not (intent := await crud.full_intent.get(db, intent_id)):
        raise exceptions.NetdriftFullIntentConfigNotFoundError(intent_id)

    return intent


@router.post("/", response_model=FullIntentConfigRead)
async def create_full_intent(db: DatabaseDep, obj_in: FullIntentConfigCreate):
    """Create a full intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        obj_in:     FullIntentConfigCreate object.
    """
    obj_created = await logic.create_full_intent(db, obj_in)
    return obj_created


@router.patch("/{intent_id}", response_model=FullIntentConfigRead)
async def update_full_intent(
    db: DatabaseDep, intent_id: PyObjectId, obj_in: FullIntentConfigUpdate
):
    """Update a full intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  Intent Id.
        obj_in:     FullIntentConfigUpdate object.
    """
    if not (existing_intent := await crud.full_intent.get(db, intent_id)):
        raise exceptions.NetdriftFullIntentConfigNotFoundError(intent_id)

    if obj_in.hostname and obj_in.hostname != existing_intent.hostname:
        raise exceptions.NetdriftIntentConfigHostnameLockError

    updated_obj = await logic.update_full_intent(db, intent_id, obj_in)
    return updated_obj


@router.delete("/{intent_id}", response_model=FullIntentConfigRead)
async def delete_full_intent(db: DatabaseDep, intent_id: PyObjectId):
    """Remove a full intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  Intent Id.
    """
    if not (existing_intent := await crud.full_intent.get(db, intent_id)):
        raise exceptions.NetdriftFullIntentConfigNotFoundError(intent_id)

    await crud.full_intent.delete(db, intent_id)
    return existing_intent
