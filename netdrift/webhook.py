import json

from aiohttp import ClientSession
from structlog import get_logger

from netdrift.models.intent import Intent
from netdrift.models.intent_diff import IntentDiff
from netdrift.models.webhook import Webhook

logger = get_logger()


async def send_intent_diff_webhook(
    webhook: Webhook, intent: Intent, intent_diff: IntentDiff
) -> None:
    """Attempts to send generic payload to webhook after a IntentDiff job has ran.

    Variables built in can be provided to replace text within the payload body. These variables include:
        - { intent_hostname } represents the hostname of the intent.
        - { intent_config_hash } represents the config_hash of the intent.
        - { intent_description } represents the description of the intent
        - { intent_last_discovery_id } represents the last_discovery_id attribute of the intent.
        - { intent_last_discovery status } represents the last_discovery_status attribute of the intent.
        - { intent_last_discovery_message } represents the last_discovery_message attribute of the intent.
        - { intent_diff } represents the diff attribute of the intent diff.
        - { intent } represents the intent of the intent/diff.
        - { intent_id } represents the id of the intent.
        - { intent_diff_id } represents the id of the intent diff.

    Args:
        webhook:        Webhook Argument.
        intent:         Intent object.
        intent_diff:    IntentDiff object.
    """
    payload_str = json.dumps(webhook.body)
    variable_map = {
        "intent_hostname": intent.hostname,
        "intent_config_hash": intent.config_hash,
        "intent_description": intent.description,
        "intent_last_discovery_id": intent.last_discovery_id,
        "intent_last_discovery_status": intent.last_discovery_status,
        "intent_last_discovery_message": intent.last_discovery_message,
        "intent_diff": intent_diff.diff,
        "intent": intent.config,
        "intent_id": intent.id,
        "intent_diff_id": intent_diff.id,
    }

    # Have to fix being able to send diff in reply
    for var in variable_map.keys():
        var_formatted = f"{{ { var } }}"
        if var_formatted in payload_str:
            normalized_variable = str(variable_map[var]).replace('"', '\\"')
            payload_str = payload_str.replace(var_formatted, normalized_variable)

    logger.debug(
        "Payload string that will be sent to webhook follows", payload_str=payload_str
    )
    payload = json.loads(payload_str)

    logger.debug("Sending HTTP webhook.", payload=payload, url=webhook.url)
    async with ClientSession(**webhook.session_kwargs) as session:
        async with session.post(
            webhook.url, json=payload, **webhook.method_kwargs
        ) as resp:
            assert resp.status == 200
