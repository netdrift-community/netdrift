from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job, JobStatus, JobDef

from netdrift.config import settings

router = APIRouter()


@router.get("/")
async def get_jobs():
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    jobs = await redis.all_job_results()
    return jobs


@router.get("/{job_id}")
async def get_job(job_id: str):
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    job = Job(job_id=job_id, redis=redis)
    return [
        job.job_id,
        await job.result_info(),
        await job.status(),
        job._queue_name,
        await job.info(),
    ]


@router.delete("/flush")
async def flush_jobs():
    redis = await create_pool(
        RedisSettings(host=settings.REDIS_HOST.host, port=settings.REDIS_HOST.port)
    )
    jobs = await redis.all_job_results()
    for job in jobs:
        arq_job = Job(job_id=job.job_id, redis=redis)
        await arq_job.abort()

    return f"Cancelled {len(jobs)} jobs"
