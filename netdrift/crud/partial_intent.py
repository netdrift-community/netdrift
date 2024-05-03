from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)
from structlog import get_logger

from netdrift.crud.base import CRUDBase
from netdrift.models.intent import (
    PartialIntentConfig,
    PartialIntentConfigCreate,
    PartialIntentConfigUpdate,
)

logger = get_logger()


class CRUDPartialIntent(
    CRUDBase[PartialIntentConfig, PartialIntentConfigCreate, PartialIntentConfigUpdate]
):
    """Basic CRUD implementation for partial intent."""

    async def get_all_by_hostname(
        self, db: AsyncIOMotorDatabase, hostname: str, skip: int = 0, limit: int = 100
    ) -> list[PartialIntentConfig]:
        """Get the PartialIntentConfig for a given hostname.

        Args:
            db:         AsyncIOMotorDatabase object.
            hostname:   hostname of device to filter.
            skip:       Offsets number of documents to skip.
            limit:      Maximum number of documents to return.
        """
        result = await self.get_multi(db, skip, limit, {"hostname": hostname})
        if not result:
            return
        return result

    async def get_all_by_config_hash(
        self,
        db: AsyncIOMotorDatabase,
        config_hash: str,
        hostname: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PartialIntentConfig]:
        """Get the PartialIntentConfig for a given config_hash and optional hostname.

        Args:
            db:             AsyncIOMotorDatabase object.
            config_hash:    Configuration hash.
            hostname:       Optional hostname of device to filter.
            skip:           Offsets number of documents to skip.
            limit:          Maximum number of documents to return.
        """
        results = await self.get_multi(
            db, skip, limit, {"hostname": hostname, "config_hash": config_hash}
        )
        if not results:
            return None
        return [self.model.model_validate(r) for r in results]

    async def get_all_by_filter_hash(
        self,
        db: AsyncIOMotorDatabase,
        filter_hash: str,
        hostname: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PartialIntentConfig]:
        """Get the PartialIntentConfig for a given config_hash and optional hostname.

        Args:
            db:             AsyncIOMotorDatabase object.
            filter_hash:    Filter hash.
            hostname:       Optional hostname of device to filter.
            skip:           Offsets number of documents to skip.
            limit:          Maximum number of documents to return.
        """
        results = await self.get_multi(
            db, skip, limit, {"hostname": hostname, "filter_hash": filter_hash}
        )
        if not results:
            return None
        return [self.model.model_validate(r) for r in results]


partial_intent = CRUDPartialIntent(
    collection="partial_intent", model=PartialIntentConfig
)
