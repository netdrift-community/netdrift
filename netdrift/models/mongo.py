"""Common models when working with Mongo database."""

from typing import Annotated, Any
from pydantic import BaseModel
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(str):
    """str representation of _id for Mongo BSON documents."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)


PyObjectId = Annotated[ObjectId, PyObjectId]


class BulkOperationResponse(BaseModel):
    acknowledged: bool
    successful_changes: int


class BaseQuery(BaseModel):
    def build_query(self) -> dict:
        return self.model_dump(exclude_unset=True, exclude_none=True)
