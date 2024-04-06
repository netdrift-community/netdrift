from enum import Enum


class IntentTypeEnum(str, Enum):
    full = "full"
    partial = "partial"


class IntentLastDiscoveryStatusEnum(str, Enum):
    unknown = "unknown"
    success = "success"
    failed = "failed"
