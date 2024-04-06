from lxml.etree import ElementBase
from xmldiff import main, formatting
from xmldiff.actions import (
    MoveNode,
    DeleteNamespace,
    DeleteNode,
    InsertNamespace,
    InsertNode,
    RenameNode,
)
from lxml import etree
from structlog import get_logger

logger = get_logger()


def diff_intent_to_config(
    intent_str: ElementBase, config_str: ElementBase
) -> ElementBase | None:
    """Attempts to build a basic XML tree of intent config to apply to NETCONF device.

    Args:
        intent:     Intent XML tree of the device configuration.
        config:     Current XML tree of the existing device configuration.
    """
    xml_parser = etree.XMLParser(
        encoding="utf-8", remove_blank_text=True, ns_clean=True
    )

    intent: list[ElementBase] = etree.XML(intent_str, xml_parser)
    config: ElementBase = etree.XML(config_str, xml_parser)

    intent_config = ""

    for intent_child in intent:
        intent_match = config.find(intent_child.tag)
        if intent_match is None:
            logger.info(
                "Root intent not found in current configuration, this will be added on the diff"
            )
            continue

        intent_diff = main.diff_trees(
            intent_match,
            intent_child,
        )

        actions = []
        for change in intent_diff:
            match change:
                case InsertNamespace():
                    if change.prefix == "nc":  # temp hacky workaround
                        logger.debug(
                            "nc prefix found in namespace insert action, skipping"
                        )
                        continue
                case _:
                    pass

            actions.append(change)

        if not actions:
            continue

        logger.info("intent found", actions=actions, intent_match=intent_match)
        intent_patch = main.patch(actions, intent_match)

        if intent_patch is None:
            continue

        patched_tree = etree.tostring(intent_patch, method="c14n2", strip_text=True)
        logger.info("tree patched", patched_tree=patched_tree[:300])
        intent_config += f"{patched_tree}\n"

    return intent_config
