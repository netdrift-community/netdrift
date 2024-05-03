from fastapi import APIRouter, Depends

from netdrift.dependencies import DatabaseDep
from netdrift.models.mongo import PyObjectId
from netdrift.models.intent_group import (
    IntentGroupRead,
    IntentGroupCreate,
    IntentGroupUpdate,
)
from netdrift import crud, exceptions, logic

router = APIRouter()


@router.get("/", response_model=list[IntentGroupRead])
async def get_all_intent_groups(
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all intent groups.

    Args:
        db:     AsyncIOMotorDatabase object.
        skip:   Offset when searching the database.
        limit:  Limit database resources returned.
    """
    intent_groups = await crud.intent_group.get_multi(db, skip, limit)
    return intent_groups


@router.get("/{group_id}", response_model=IntentGroupRead)
async def get_intent_group(db: DatabaseDep, group_id: PyObjectId):
    """Get a specific intent group.

    Args:
        db:         AsyncIOMotorDatabase object.
        group_id:   Group Id.
    """
    if not (intent_group := await crud.intent_group.get(db, group_id)):
        raise exceptions.NetdriftIntentGroupNotFoundError(group_id)

    return intent_group


@router.post("/", response_model=IntentGroupRead)
async def create_intent_group(db: DatabaseDep, obj_in: IntentGroupCreate):
    """Create an IntentGroup.

    Args:
        db:         AsyncIOMotorDatabase object.
        obj_in:     IntentGroupCreate object.
    """
    obj_created = await logic.create_intent_group(db, obj_in)
    return obj_created


@router.patch("/{group_id}", response_model=IntentGroupRead)
async def update_intent_group(
    db: DatabaseDep, group_id: PyObjectId, obj_in: IntentGroupUpdate
):
    """Update an IntentGroup.

    Args:
        db:         AsyncIOMotorDatabase object.
        group_id:   Group Id.
        obj_in:     IntentGroupUpdate object.
    """
    if not (existing_intent_group := await crud.intent_group.get(db, group_id)):
        raise exceptions.NetdriftIntentGroupNotFoundError(group_id)

    updated_obj = await logic.update_intent_group(db, group_id, obj_in)
    return updated_obj


@router.delete("/{group_id}", response_model=IntentGroupRead)
async def delete_intent_group(db: DatabaseDep, group_id: PyObjectId):
    """Remove an IntentGroup.

    Args:
        db:         AsyncIOMotorDatabase object.
        group_id:   Group Id.
    """
    if not (existing_intent_group := await crud.intent_group.get(db, group_id)):
        raise exceptions.NetdriftIntentGroupNotFoundError(group_id)

    await crud.intent_group.delete(db, group_id)
    return existing_intent_group
