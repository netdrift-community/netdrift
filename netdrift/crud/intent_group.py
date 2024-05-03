from bson.objectid import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)
from structlog import get_logger

from netdrift.crud.base import CRUDBase
from netdrift.models.intent_group import (
    IntentGroup,
    IntentGroupCreate,
    IntentGroupUpdate,
)

logger = get_logger()


class CRUDIntentGroup(CRUDBase[IntentGroup, IntentGroupCreate, IntentGroupUpdate]):
    """Basic CRUD implementation for an intent_group."""

    async def get_by_label(self, db: AsyncIOMotorDatabase, label: str) -> IntentGroup:
        """Get a specific IntentGroup based on the label.

        Args:
            db:         AsyncIOMotorDatabase object.
            label:      Label of the IntentGroup.
        """
        result = await self.get_filter(db, {"label": label})
        if not result:
            return

        return self.model.model_validate(result)

    async def get_all_by_hostname(
        self, db: AsyncIOMotorDatabase, hostname: str, skip: int = 0, limit: int = 100
    ) -> list[IntentGroup]:
        """Get all IntentGroups for a given hostname.

        Args:
            db:         AsyncIOMotorDatabase object.
            hostname:   Hostname of device to filter.
            skip:       Offsets number of documents to skip.
            limit:      Maximum number of documents to return.
        """
        results = await self.get_multi(db, skip, limit, {"hostname": hostname})
        if not results:
            return None

        return [self.model.model_validate(r) for r in results]


intent_group = CRUDIntentGroup(collection="intent_group", model=IntentGroup)
