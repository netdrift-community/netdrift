from fastapi import APIRouter, Depends

from netdrift.dependencies import DatabaseDep
from netdrift.models.mongo import PyObjectId
from netdrift.models.intent import (
    PartialIntentConfigQuery,
    PartialIntentConfigRead,
    PartialIntentConfigCreate,
    PartialIntentConfigUpdate,
)
from netdrift import crud, exceptions, logic

router = APIRouter()


@router.get("/", response_model=list[PartialIntentConfigRead])
async def get_all_partial_intent(
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
    params: PartialIntentConfigQuery = Depends(),
):
    """Get all partial intents.

    Args:
        db:     AsyncIOMotorDatabase object.
        skip:   Offset when searching the database.
        limit:  Limit database resources returned.
        params: Query params.
    """
    param_query = params.build_query()
    intents = await crud.partial_intent.get_multi(db, skip, limit, param_query)
    return intents


@router.get("/{intent_id}", response_model=PartialIntentConfigRead)
async def get_partial_intent(db: DatabaseDep, intent_id: PyObjectId):
    """Get a specific partial intent.

    Args:
        db:             AsyncIOMotorDatabase object.
        intent_id:      Intent Id.
    """
    if not (intent := await crud.partial_intent.get(db, intent_id)):
        raise exceptions.NetdriftPartialIntentConfigNotFoundError(intent_id)

    return intent


@router.post("/", response_model=PartialIntentConfigRead)
async def create_partial_intent(db: DatabaseDep, obj_in: PartialIntentConfigCreate):
    """Create a partial intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        obj_in:     PartialIntentConfigCreate object.
    """
    obj_created = await logic.create_partial_intent(db, obj_in)
    return obj_created


@router.patch("/{intent_id}", response_model=PartialIntentConfigRead)
async def update_partial_intent(
    db: DatabaseDep, intent_id: PyObjectId, obj_in: PartialIntentConfigUpdate
):
    """Update a partial intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  Intent Id.
        obj_in:     PartialIntentConfigUpdate object.
    """
    if not (existing_intent := await crud.partial_intent.get(db, intent_id)):
        raise exceptions.NetdriftPartialIntentConfigNotFoundError(intent_id)

    if obj_in.hostname and obj_in.hostname != existing_intent.hostname:
        raise exceptions.NetdriftIntentConfigHostnameLockError

    updated_obj = await logic.update_partial_intent(db, intent_id, obj_in)
    return updated_obj


@router.delete("/{intent_id}", response_model=PartialIntentConfigRead)
async def delete_partial_intent(db: DatabaseDep, intent_id: PyObjectId):
    """Remove a partial intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  Intent Id.
    """
    if not (existing_intent := await crud.partial_intent.get(db, intent_id)):
        raise exceptions.NetdriftPartialIntentConfigNotFoundError(intent_id)

    await crud.partial_intent.delete(db, intent_id)
    return existing_intent
