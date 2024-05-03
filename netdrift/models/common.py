"""Common data models used in netdrift."""

from pydantic import BaseModel, ConfigDict


class NetdriftModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, validate_assignment=True
    )
