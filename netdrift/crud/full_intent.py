from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)
from structlog import get_logger

from netdrift.crud.base import CRUDBase
from netdrift.models.intent import (
    FullIntentConfig,
    FullIntentConfigCreate,
    FullIntentConfigUpdate,
)

logger = get_logger()


class CRUDFullIntent(
    CRUDBase[FullIntentConfig, FullIntentConfigCreate, FullIntentConfigUpdate]
):
    """Basic CRUD implementation for full intent."""

    async def get_by_hostname(
        self, db: AsyncIOMotorDatabase, hostname: str
    ) -> FullIntentConfig:
        """Get the FullIntentConfig for a given hostname.

        Args:
            db:         AsyncIOMotorDatabase object.
            hostname:   hostname of device to filter.
        """
        result = await self.get_filter(db, {"hostname": hostname})
        if not result:
            return
        return self.model.model_validate(result)


full_intent = CRUDFullIntent(collection="full_intent", model=FullIntentConfig)
