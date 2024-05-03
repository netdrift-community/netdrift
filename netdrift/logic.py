from hashlib import sha256
from lxml import etree as ET
from lxml.etree import _Element as Element

from motor.motor_asyncio import AsyncIOMotorDatabase
from structlog import get_logger

from netdrift.models.intent import (
    FullIntentConfig,
    FullIntentConfigCreate,
    FullIntentConfigUpdate,
    PartialIntentConfig,
    PartialIntentConfigCreate,
    PartialIntentConfigUpdate,
)
from netdrift.models.intent_group import (
    IntentGroup,
    IntentGroupCreate,
)
from netdrift.models.mongo import PyObjectId
from netdrift import crud
from netdrift import exceptions

logger = get_logger()


async def create_full_intent(
    db: AsyncIOMotorDatabase, intent: FullIntentConfigCreate
) -> FullIntentConfig:
    """Logic implementation to create a full intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent:     FullIntentConfigCreate object.
    """
    logger.debug("Attempting to create a FullIntentConfig object in the database.")
    # Check if intent with hostname already exist
    if await crud.full_intent.get_by_hostname(db, intent.hostname):
        raise exceptions.NetdriftFullIntentConfigAlreadyExistError

    # Validate, format, update and finally hash config attribute if present
    xml_obj = validate_xml(intent.config)
    formatted_xml = format_xml(xml_obj)
    config_hash = sha256(formatted_xml)

    intent.config = formatted_xml
    intent.config_hash = config_hash.hexdigest()

    obj_in_db = await crud.full_intent.create(db, intent)
    return obj_in_db


async def create_partial_intent(
    db: AsyncIOMotorDatabase, intent: PartialIntentConfigCreate
) -> PartialIntentConfig:
    """Logic implementation to create a partial intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent:     PartialIntentConfigCreate object.
    """
    logger.debug("Attempting to create a PartialIntentConfig object in the database.")

    # Validate, format, update and finally hash config attribute if present
    xml_obj = validate_xml(intent.config)
    formatted_xml = format_xml(xml_obj)
    config_hash = sha256(formatted_xml)

    intent.config = formatted_xml
    intent.config_hash = config_hash.hexdigest()

    # Check if there is already a PartialIntent based on config-hash and hostname (including None)
    if await crud.partial_intent.get_all_by_config_hash(
        db, intent.config_hash, intent.hostname
    ):
        raise exceptions.NetdriftPartialIntentConfigAlreadyExistError

    # Check if filter is valid
    xml_filter_obj = validate_xml(intent.filter)
    formatted_xml_filter = format_xml(xml_filter_obj)
    config_filter_hash = sha256(formatted_xml_filter)

    intent.filter_hash = config_filter_hash.hexdigest()

    # Check if filter is already being managed by another intent for the same hostname (including None)
    if await crud.partial_intent.get_all_by_filter_hash(
        db, intent.filter_hash, intent.hostname
    ):
        raise exceptions.NetdriftPartialIntentConfigFilterAlreadyExistError

    # Advanced check to strip all namespaces from the filter to see if this is also already being managed by another intent for the same hostname (including None)
    # TBI

    obj_in_db = await crud.partial_intent.create(db, intent)
    return obj_in_db


async def create_intent_group(
    db: AsyncIOMotorDatabase, intent_group: IntentGroupCreate
) -> IntentGroup:
    """Logic implementation to create an IntentGroup.

    Args:
        db:             AsyncIOMotorDatabase object.
        intent_group:   IntentGroupCreate object.
    """
    if await crud.intent_group.get_by_label(db, intent_group.label):
        raise exceptions.NetdriftIntentGroupAlreadyExistError

    # Check all partial intents exist and none are assosicated to a hostname if we don't have a hostname set
    # if the hostname attribute is set, all inherited PartialIntentConfig objects hostname attribute must match if its set.
    intents_managed = []

    if intent_group.intents:
        intents = []

        for intent in intent_group.intents:
            if intent in intents_managed:
                raise exceptions.NetdriftIntentGroupIntentDuplicationError

            if not (existing_intent := await crud.partial_intent.get(db, intent)):
                raise exceptions.NetdriftPartialIntentConfigNotFoundError(intent)

            if not intent_group.hostname and existing_intent.hostname:
                raise exceptions.NetdriftIntentGroupHostnameManagedError  # need to review
            elif (
                intent_group.hostname
                and existing_intent.hostname
                and intent_group.hostname != existing_intent.hostname
            ):
                raise exceptions.NetdriftIntentGroupHostnameMismatchError  # need to review

            intents_managed.append(existing_intent.id)
            intents.append(existing_intent)

        intent_group.intents = intents

    # Check all intentgroups exist and none are assosicated to a hostname if we don't have a hostname set
    # if the hostname attribute is set, all inherited IntentGroup objects hostname attribute must match if its set.
    if intent_group.groups:
        groups = []

        for group in intent_group.groups:
            if not (existing_intent_group := await crud.intent_group.get(db, group)):
                raise exceptions.NetdriftIntentGroupNotFoundError(group)

            if not intent_group.hostname and existing_intent_group.hostname:
                raise exceptions.NetdriftIntentGroupHostnameManagedError  # need to review
            elif (
                intent_group.hostname
                and existing_intent_group.hostname
                and intent_group.hostname != existing_intent_group.hostname
            ):
                raise exceptions.NetdriftIntentGroupHostnameMismatchError  # need to review

            # Check inherited intents are not being managed directly
            for inherited_intent in existing_intent_group.intents:
                if inherited_intent.id in intents_managed:
                    raise exceptions.NetdriftIntentGroupIntentDuplicationError

                intents_managed.append(inherited_intent.id)

            groups.append(existing_intent_group)

        intent_group.groups = groups

    obj_in_db = await crud.intent_group.create(db, intent_group)
    return obj_in_db


async def update_partial_intent(
    db: AsyncIOMotorDatabase,
    intent_id: PyObjectId,
    intent: PartialIntentConfigUpdate,
) -> PartialIntentConfig:
    """Logic implementation to update a partial intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  PartialIntentConfig id to search for.
        intent:     PartialIntentConfigUpdate object.
    """
    logger.debug("Attempting to update a PartialIntentConfig object in the database.")
    if not (existing_intent := await crud.partial_intent.get(db, intent_id)):
        raise exceptions.NetdriftPartialIntentConfigNotFoundError(intent_id)

    # Don't allow people to update the database ID
    if intent.id and intent.id != existing_intent.id:
        raise exceptions.NetdriftPartialIntentConfigUpdateError

    # Don't allow people to update the hostname
    if intent.netdrift_managed != existing_intent.netdrift_managed:
        raise exceptions.NetdriftIntentConfigAPILockError

    if intent.config:
        # Validate, format, update and finally hash config attribute if present
        xml_obj = validate_xml(intent.config)
        formatted_xml = format_xml(xml_obj)
        config_hash = sha256(formatted_xml)

        intent.config = formatted_xml
        intent.config_hash = config_hash.hexdigest()

    if intent.filter:
        # Validate, format, update and finally hash config attribute if present
        xml_filter_obj = validate_xml(intent.filter)
        formatted_filter_xml = format_xml(xml_filter_obj)
        filter_hash = sha256(formatted_filter_xml)

        intent.filter = formatted_filter_xml
        intent.filter_hash = filter_hash.hexdigest()

    updated_obj = await crud.partial_intent.update(
        db, intent_id, existing_intent, intent
    )
    return updated_obj


async def update_intent_group(
    db: AsyncIOMotorDatabase, group_id: PyObjectId, intent_group: IntentGroupCreate
) -> IntentGroup:
    """Logic implementation to update an IntentGroup.

    Args:
        db:             AsyncIOMotorDatabase object.
        group_id:       IntentGroup id to search for.
        intent_group:   IntentGroupCreate object.
    """
    raise NotImplementedError


async def update_full_intent(
    db: AsyncIOMotorDatabase,
    intent_id: PyObjectId,
    intent: FullIntentConfigUpdate,
) -> FullIntentConfig:
    """Logic implementation to update a full intent.

    Args:
        db:         AsyncIOMotorDatabase object.
        intent_id:  FullIntentConfig id to search for.
        intent:     FullIntentConfigUpdate object.
    """
    logger.debug("Attempting to update a FullIntentConfig object in the database.")
    if not (existing_intent := await crud.full_intent.get(db, intent_id)):
        raise exceptions.NetdriftFullIntentConfigNotFoundError(intent_id)

    # Don't allow people to update the database ID
    if intent.id and intent.id != existing_intent.id:
        raise exceptions.NetdriftFullIntentConfigUpdateError

    # Don't allow people to update the hostname
    if intent.netdrift_managed != existing_intent.netdrift_managed:
        raise exceptions.NetdriftIntentConfigAPILockError

    if intent.config:
        # Validate, format, update and finally hash config attribute if present
        xml_obj = validate_xml(intent.config)
        formatted_xml = format_xml(xml_obj)
        config_hash = sha256(formatted_xml)

        intent.config = formatted_xml
        intent.config_hash = config_hash.hexdigest()

    updated_obj = await crud.full_intent.update(db, intent_id, existing_intent, intent)
    return updated_obj


def validate_xml(config: str) -> Element:
    """Attempts to validate given XML string and returns back as an Element.

    Args:
        config:             XML string.
    """
    logger.debug("Attempting to validate an XML string.")
    try:
        xml_object = ET.XML(config)
    except Exception as err:
        logger.error("XML is invalid.", error=err)
        raise exceptions.NetdriftXMLParserError(err)

    return xml_object


def format_xml(config_xml: Element) -> str:
    """Attempts to format lxml Element for the netdrift database.

    This function attempts to consolidate the XML string into a minimal single line string using
    Canonical 2.0 formatting.

    Args:
        config_xml:     XML string.
    """
    logger.debug("Attempting to format an XML Element.")
    if isinstance(config_xml, str):
        config_xml = validate_xml(config_xml)

    # Reformat in Canonical XML 2.0 format without pretty-print to reduce size in database
    try:
        formatted_config = ET.tostring(
            config_xml, pretty_print=False, strip_text=True, method="c14n2"
        )
    except Exception as err:
        logger.error(
            "Unable to re-format XML to Canonical 2.0 format.",
            error=err,
        )
        raise exceptions.NetdriftXMLParserError(err)

    return formatted_config
