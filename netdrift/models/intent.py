from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from netdrift.models.common import NetdriftModel
from netdrift.models.mongo import PyObjectId, QueryBase


class IntentBase(NetdriftModel):
    id: PyObjectId | None = Field(default=None, alias="_id", serialization_alias="id")
    hostname: Annotated[str, StringConstraints(min_length=1)] | None = None
    netdrift_managed: bool = False
    config: Annotated[str, StringConstraints(min_length=1)] | None = None
    config_hash: Annotated[str, StringConstraints(min_length=1)] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IntentQueryBase(QueryBase):
    config_hash: str | None = None


class FullIntentConfigBase(IntentBase):
    pass


class FullIntentConfigQuery(IntentQueryBase):
    pass


class FullIntentConfigRead(FullIntentConfigBase):
    pass


class FullIntentConfigCreate(FullIntentConfigBase):
    hostname: Annotated[str, StringConstraints(min_length=1)]
    config: Annotated[str, StringConstraints(min_length=1)]
    created_at: datetime = Field(default_factory=datetime.now)


class FullIntentConfigUpdate(FullIntentConfigBase):
    updated_at: datetime = Field(default_factory=datetime.now)


class FullIntentConfig(FullIntentConfigBase):
    pass


class PartialIntentConfigBase(IntentBase):
    filter: str | None = None
    filter_hash: str | None = None


class PartialIntentConfigQuery(IntentQueryBase):
    hostname: str | None = None
    config_hash: str | None = None
    filter: str | None = None
    filter_hash: str | None = None


class PartialIntentConfigRead(PartialIntentConfigBase):
    pass


class PartialIntentConfigCreate(PartialIntentConfigBase):
    config: Annotated[str, StringConstraints(min_length=1)]
    filter: Annotated[str, StringConstraints(min_length=1)]
    created_at: datetime = Field(default_factory=datetime.now)


class PartialIntentConfigUpdate(PartialIntentConfigBase):
    updated_at: datetime = Field(default_factory=datetime.now)


class PartialIntentConfig(PartialIntentConfigBase):
    pass


class PartialIntentConfigShort(NetdriftModel):
    id: PyObjectId | None = Field(default=None, alias="_id", serialization_alias="id")
    hostname: str | None = None
    config_hash: str
    filter_hash: str


class IntentGroupBase(NetdriftModel):
    pass
