from datetime import datetime

from pydantic import Field, BaseModel

from netdrift.models.common import DeviceAuthentication, NetdriftModel
from netdrift.models.mongo import PyObjectId, BaseQuery
from netdrift.models.enums import IntentLastDiscoveryStatusEnum, IntentTypeEnum
from netdrift.models.webhook import Webhook


class IntentBase(NetdriftModel):
    id: PyObjectId | None = Field(default=None, alias="_id")
    hostname: str | None = None
    description: str | None = None
    config_hash: str | None = None
    type: IntentTypeEnum | None = None
    filter: str | None = None
    last_discovery_id: str | None = None
    last_discovery_status: IntentLastDiscoveryStatusEnum | None = None
    last_discovery_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IntentCreate(IntentBase):
    hostname: str
    type: IntentTypeEnum = IntentTypeEnum.full
    config: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class IntentUpdate(IntentBase):
    config: str | None = None
    updated_at: datetime = Field(default_factory=datetime.now)


class IntentRead(IntentBase):
    pass


class Intent(IntentBase):
    config: str | None = None


class IntentQuery(BaseQuery):
    hostname: str | None = None
    filter: str | None = None
    type: IntentTypeEnum | None = None
    config_hash: str | None = None
    last_discovery_status: IntentLastDiscoveryStatusEnum | None = None


class IntentJob(BaseModel):
    intent: Intent
    auth: DeviceAuthentication
    webhook: Webhook | None = None
