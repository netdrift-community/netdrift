from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)


from netdrift.crud.base import CRUDBase
from netdrift.models.intent import Intent, IntentCreate, IntentUpdate
from netdrift.models.enums import IntentTypeEnum


class CRUDIntent(CRUDBase[Intent, IntentCreate, IntentUpdate]):
    """Basic CRUD implementation for intent."""

    async def get_intent_by_hostname(
        self, db: AsyncIOMotorDatabase, hostname: str
    ) -> Intent:
        """Get the intent of a specific device configuration based on hostname.

        Args:
            db:         AsyncIOMotorDatabase object.
            hostname:   Hostname of device to filter by.
        """
        result = await db[self.collection].find_one({"hostname": hostname})
        if not result:
            return

        return self.model.model_validate(result)

    async def get_all_intent_by_hostname(
        self,
        db: AsyncIOMotorDatabase,
        hostname: str,
        type: IntentTypeEnum | None = None,
    ) -> list[Intent]:
        """Attempts to get all intent for a specific hostname.

        Args:
            db:         AsyncIOMotorDatabase object.
            hostname:   Hostname of device to filter by.
            type:       Intent type (full vs partial), if empty all intent is returned.
        """
        query = {"hostname": hostname}
        if type:
            query["type"] = type

        intents = []
        async for result in db[self.collection].find(query):
            intents.append(result)

        return intents


intent = CRUDIntent(collection="intent", model=Intent)
