from pydantic import Field

from netdrift.models.common import NetdriftModel
from netdrift.models.mongo import PyObjectId
from netdrift.models.intent import PartialIntentConfig


class IntentGroupBase(NetdriftModel):
    id: PyObjectId | None = Field(default=None, alias="_id", serialization_alias="id")
    label: str | None = Field(
        None, description="User friendly label to identify the IntentGroup."
    )
    description: str | None = Field(
        None, description="Description to describe the purpose of the IntentGroup"
    )
    hostname: str | None = None
    intents: list[PartialIntentConfig] | None = None
    groups: list["IntentGroup"] | None = None


class IntentGroupCreate(IntentGroupBase):
    label: str
    intents: list[PartialIntentConfig | PyObjectId] | None = []
    groups: list["IntentGroup" | PyObjectId] | None = []


class IntentGroupUpdate(IntentGroupBase):
    pass


class IntentGroupRead(IntentGroupBase):
    pass


class IntentGroup(IntentGroupBase):
    intents: list[PartialIntentConfig] = []
    groups: list["IntentGroup"] = []
