from hashlib import sha256
from lxml import etree
from difflib import Differ

from arq.connections import RedisSettings
from structlog import get_logger

from ncclient import manager

# from ncdiff import manager, ConfigDelta
from ncclient.transport.errors import SSHError

from netdrift.config import settings
from netdrift.models.intent import IntentJob, IntentUpdate
from netdrift.models.intent_diff import IntentDiffCreate
from netdrift.models.enums import IntentLastDiscoveryStatusEnum, IntentTypeEnum
from netdrift.dependencies import db
from netdrift.webhook import send_intent_diff_webhook
from netdrift import crud

logger = get_logger()


async def create_intent(ctx: dict, job: IntentJob) -> None:
    """Creates a full or partial intent.

    Args:
        ctx:    ARQ content.
        job:    Intent Job.
    """
    logger.info(
        f"Attempting to create intent for {job.intent.hostname} ({job.intent.type})"
    )
    intent = job.intent
    update_obj = IntentUpdate()

    try:
        with manager.connect(
            host=intent.hostname,
            username=job.auth.username,
            password=job.auth.password,
            hostkey_verify=False,
        ) as c:
            config = c.get_config(
                source="running",
                filter=None
                if intent.type == IntentTypeEnum.full
                else ("subtree", intent.filter),
            )
            config_xml = etree.tostring(
                config.data, pretty_print=False, strip_text=True, method="c14n2"
            )
            config_hash = sha256(config_xml)

            update_obj.config_hash = config_hash.hexdigest()
            update_obj.config = config_xml
            update_obj.last_discovery_status = IntentLastDiscoveryStatusEnum.success
            update_obj.last_discovery_message = (
                "Intent resynced and updated config hash."
            )

    except SSHError as err:
        msg = f"Unable to setup transport to '{intent.hostname}' due to error: {err}"
        logger.error(msg)
        update_obj.last_discovery_status = IntentLastDiscoveryStatusEnum.failed
        update_obj.last_discovery_message = msg
        return

    database = await db()
    await crud.intent.update(database, intent.id, intent, update_obj)

    return


async def intent_diff(ctx: dict, job: IntentJob) -> None:
    """Attempts to diff intend and existing configuration.

    Args:
        ctx:    ARQ content.
        job:    Intent Job.
    """
    logger.info("Attempting to diff intent")
    intent = job.intent
    no_diff = False

    # Can not continue if filter does not exist
    if not intent.filter:
        raise ValueError("filter must be present to allow intent diffs")

    try:
        with manager.connect(
            host=intent.hostname,
            username=job.auth.username,
            password=job.auth.password,
            hostkey_verify=False,
        ) as c:
            reply = c.get_config(
                source="running",
                filter=(
                    "subtree",
                    intent.filter,
                ),
            )

            config_xml = etree.tostring(
                reply.data, pretty_print=False, strip_text=True, method="c14n2"
            )

            config_hash = sha256(config_xml)
            if config_hash.hexdigest() == intent.config_hash:
                no_diff = True

            # /router/bgp/asn/neighbors/*
            # /interfaces/interface/subint0/*
            # /interfaces/interface/subint1/*

    except SSHError as err:
        msg = f"Unable to setup transport to '{intent.hostname}' due to error: {err}"
        logger.error(msg)

    if not no_diff:
        logger.info("Before formatting", config=config_xml, intent=intent.config)

        # Sorry not sorry
        config_formatted = etree.tostring(
            etree.XML(config_xml), pretty_print=True
        ).decode("utf-8")
        intent_formatted = etree.tostring(
            etree.XML(intent.config), pretty_print=True
        ).decode("utf-8")

        diff = Differ()
        results = diff.compare(
            config_formatted.splitlines(), intent_formatted.splitlines()
        )
        diff_str = "\n".join(results)
        logger.info("Device is out of sync.")
        logger.debug(
            "Configuration to remove/add/change to get back to intent", diff=diff_str
        )

        # Save changes in diff collection so user can query what changes need to be made to fix the issue
        intent_diff_job = IntentDiffCreate(
            intent_id=intent.id, diff=diff_str, intent=intent.config
        )
        database = await db()
        intent_diff = await crud.intent_diff.create(db=database, obj_in=intent_diff_job)

        if job.webhook:
            await send_intent_diff_webhook(job.webhook, intent, intent_diff)
    else:
        logger.info("Device is in sync with intent.")

    return


class WorkerSettings:
    functions = [create_intent, intent_diff]
    redis_settings = RedisSettings(settings.REDIS_HOST.host, settings.REDIS_HOST.port)
