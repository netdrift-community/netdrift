from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)


from netdrift.crud.base import CRUDBase
from netdrift.models.intent_diff import IntentDiff, IntentDiffCreate


class CRUDIntent(CRUDBase[IntentDiff, IntentDiffCreate, None]):
    """Basic CRUD implementation for intent diff."""

    async def get_diffs_for_intent(
        self, db: AsyncIOMotorDatabase, intent_id: str, skip: int = 0, limit: int = 100
    ) -> list[IntentDiff]:
        """Attempts to gather all intent diffs ran for a specific intent_id.

        Args:
            db:         AsyncIOMotorDatabase object.
            intend_id:  ID of the intent to filter.
        """
        diffs = await self.get_multi(
            db=db, skip=skip, limit=limit, query={"intent_id": str(intent_id)}
        )
        return diffs


intent_diff = CRUDIntent(collection="intent_diff", model=IntentDiff)
