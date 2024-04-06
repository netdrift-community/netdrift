from uuid import uuid4
from lxml import etree

from fastapi import APIRouter, HTTPException, status, Depends
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job, JobStatus


from netdrift.config import settings
from netdrift.dependencies import DatabaseDep
from netdrift.models.common import DeviceAuthentication
from netdrift.models.mongo import PyObjectId
from netdrift.models.intent import (
    Intent,
    IntentRead,
    IntentCreate,
    IntentUpdate,
    IntentJob,
    IntentQuery,
)
from netdrift.models.webhook import Webhook
from netdrift.models.enums import IntentTypeEnum
from netdrift import crud

router = APIRouter()


@router.get("/{intent_id}", response_model=Intent)
async def get_intent(db: DatabaseDep, intent_id: PyObjectId):
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    return existing_intent


@router.get("/{intent_id}/diffs")
async def get_intent_diffs(
    db: DatabaseDep, intent_id: PyObjectId, skip: int = 0, limit: int = 100
):
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    all_intents = await crud.intent_diff.get_diffs_for_intent(
        db=db, intent_id=existing_intent.id, skip=skip, limit=limit
    )
    return all_intents


@router.get("/", response_model=list[IntentRead])
async def get_intents(
    db: DatabaseDep,
    query_params: IntentQuery = Depends(),
    skip: int = 0,
    limit: int = 100,
):
    existing_intents = await crud.intent.get_multi(
        db, skip, limit, query=query_params.build_query()
    )
    return existing_intents


@router.post("/", response_model=IntentRead)
async def create_intent(
    db: DatabaseDep, intent: IntentCreate, auth: DeviceAuthentication
) -> None:
    # Only 1 full intent is allowed per device
    if intent.type == IntentTypeEnum.full:
        if await crud.intent.get_all_intent_by_hostname(
            db, intent.hostname, IntentTypeEnum.full
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "There is already a full intent configured for the device.",
            )
    else:
        if not intent.filter:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "partial intent must include a filter to track the configuration intent.",
            )

        # Perform check here on partial intents to confirm filter isn't already tracked in another intent for the same device
        if await crud.intent.get_multi(
            db=db, query={"hostname": intent.hostname, "filter": intent.filter}
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "partial intent with filter already exist"
            )

        # Validate filter is at least valid XML
        try:
            etree.XML(intent.filter)
        except Exception as err:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Unable to validate filter due to error: {err}",
            )

    job_id = str(uuid4())
    intent.last_discovery_id = job_id

    intent_created = await crud.intent.create(db, intent)

    # Create intent job to pass to worker
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    await redis.enqueue_job(
        "create_intent",
        IntentJob(intent=intent_created, auth=auth),
        _job_id=str(job_id),
    )

    return intent_created


@router.patch("/{intent_id}", response_model=IntentRead)
async def update_intent(
    db: DatabaseDep, intent_id: PyObjectId, intent: IntentUpdate
) -> None:
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    if (
        existing_intent.type == IntentTypeEnum.partial
        and intent.type == IntentTypeEnum.full
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Unable to update a partial intent to a full intent, you should create a full intent separately.",
        )

    updated_intent = await crud.intent.update(
        db, existing_intent.id, existing_intent, intent
    )
    return updated_intent


@router.delete("/{intent_id}", response_model=IntentRead)
async def delete_intent(db: DatabaseDep, intent_id: PyObjectId) -> None:
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    await crud.intent.delete(db, existing_intent.id)
    return existing_intent


@router.post("/{intent_id}/diff", response_model=IntentRead)
async def diff_intent(
    db: DatabaseDep,
    intent_id: PyObjectId,
    auth: DeviceAuthentication,
    webhook: Webhook | None = None,
) -> None:
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    job_id = str(uuid4())

    # Update database

    # Create intent job to pass to worker
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    job = IntentJob(intent=existing_intent, auth=auth)
    if webhook:
        job.webhook = webhook

    await redis.enqueue_job(
        "intent_diff",
        job,
        _job_id=str(job_id),
    )

    return existing_intent


@router.post("/{intent_id}/sync", response_model=IntentRead)
async def resync_intent_for_device(
    db: DatabaseDep, intent_id: PyObjectId, auth: DeviceAuthentication
) -> None:
    if not (existing_intent := await crud.intent.get(db, intent_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Unable to find an Intent for this intent_id."
        )

    job_id = str(uuid4())
    existing_intent.last_discovery_id = job_id

    # Update last discovery id
    await crud.intent.update(db, existing_intent.id, existing_intent, existing_intent)

    # Create intent job to pass to worker
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    await redis.enqueue_job(
        "create_intent",
        IntentJob(intent=existing_intent, auth=auth),
        _job_id=str(job_id),
    )

    return existing_intent
