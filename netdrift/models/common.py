from pydantic import BaseModel, ConfigDict


class NetdriftModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class DeviceAuthentication(BaseModel):
    username: str
    password: str
