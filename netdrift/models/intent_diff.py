from datetime import datetime

from pydantic import Field, BaseModel

from netdrift.models.common import NetdriftModel
from netdrift.models.mongo import PyObjectId, BaseQuery


class IntentDiffBase(NetdriftModel):
    id: PyObjectId | None = Field(default=None, alias="_id")
    intent_id: PyObjectId
    diff: str
    intent: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IntentDiffCreate(IntentDiffBase):
    created_at: datetime = Field(default_factory=datetime.now)


class IntentDiff(IntentDiffBase):
    pass
