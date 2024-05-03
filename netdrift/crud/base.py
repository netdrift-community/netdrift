"""CRUD Base for any module that utilizes MongoDB (motor asyncio).

This base class is a core base building block to improve the developing experience
with autocompletion, type hints and other editor features.
"""

from typing import Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.errors import WriteError, OperationFailure, PyMongoError
from bson.objectid import ObjectId
from structlog import get_logger

logger = get_logger()

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Simple CRUD class to be used with all database models.

    This class can be extended for each MongoDB collection you create and
    override the logic for example, calling a hash_password function when
    creating a user within the CRUD implementation itself.
    """

    def __init__(self, collection: AsyncIOMotorCollection, model: Type[ModelType]):
        """Base CRUD class that can be extended.

        Args:
            collection:     MongoDB Collection.
            model:          Model used in typehints and various database operations.
        """
        self.collection = collection
        self.model = model

    async def get(self, db: AsyncIOMotorDatabase, id: str) -> Optional[ModelType]:
        """Get a single Record from the Mongo Database.

        Args:
            db:     AsyncIOMotorDatabase object.
            id:     Mongo Record _id
        """
        result = await db[self.collection].find_one({"_id": ObjectId(id)})
        if not result:
            return None

        return self.model.model_validate(result)

    async def get_filter(
        self, db: AsyncIOMotorDatabase, query: dict
    ) -> Optional[ModelType]:
        """Get a single Record from the Mongo Database based on the filter.

        Args:
            db:     AsyncIOMotorDatabase object.
            query:  Query filter.
        """
        result = await db[self.collection].find_one(query)
        if not result:
            return None

        return self.model.model_validate(result)

    async def get_multi(
        self,
        db: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 100,
        query: dict = {},
    ) -> Optional[List[ModelType]]:
        """Gets multiple Records from the Database.

        Args:
            db:         AsyncIOMotorDatabase object.
            skip:       Offsets number of documents to skip.
            limit:      Maximum number of documents to return.
            query:      Optional query to filter the collection.
        """
        results = await db[self.collection].find(query).skip(skip).to_list(length=limit)
        if not results:
            return []

        return [self.model.model_validate(result) for result in results]

    async def create(
        self, db: AsyncIOMotorDatabase, obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a record in the database.

        Note that jsonable_encoder is used to handle non-jsonable fields which
        are not handled by the pydantic model

        Args:
            db:         AsyncIOMotorDatabase object.
            obj_in:     Pydantic Object to create in Database.
        """
        try:
            result = await db[self.collection].insert_one(
                obj_in.model_dump(by_alias=True, exclude_none=True)
            )
        except WriteError as err:
            logger.error(
                f"Caught WriteError while attempting to insert a resource in the database: {err}"
            )
            raise err
        except OperationFailure as err:
            logger.error(
                f"Caught OperationalFailure while attempting to insert a resource in the database: {err}"
            )
            raise err
        except PyMongoError as err:
            logger.error(
                f"Caught generic PyMongoError while attempting to insert a resource in the database: {err}"
            )
            raise err
        except Exception as err:
            logger.error(
                f"Caught unhandled exception while attempting to insert a resource in the database: {err}"
            )
            raise err

        refreshed_object = await self.get(db=db, id=result.inserted_id)
        return self.model.model_validate(refreshed_object)

    async def create_many(
        self, db: AsyncIOMotorDatabase, objs_in: List[CreateSchemaType]
    ) -> ModelType:
        """Creates multiple records in the database (bulk).

        Note that jsonable_encoder is used to handle non-jsonable fields which
        are not handled by the pydantic model

        Args:
            db:         AsyncIOMotorDatabase object.
            objs_in:    Pydantic Object(s) to create in Database.
        """
        try:
            result = await db[self.collection].insert_many(
                [obj.model_dump(exclude_none=True) for obj in objs_in]
            )
        except WriteError as err:
            logger.error(
                f"Caught WriteError while attempting to insert a resource into the database: {err}"
            )
            raise err
        except OperationFailure as err:
            logger.error(
                f"Caught OperationalFailure while attempting to insert a resource into the database: {err}"
            )
            raise err
        except PyMongoError as err:
            logger.error(
                f"Caught PyMongoError while attempting to insert a resource into the database: {err}"
            )
            raise err
        except Exception as err:
            logger.error(
                f"Caught unhandled exception while attempting to insert a resource into the database: {err}"
            )
            raise err
        return result

    async def update(
        self,
        db: AsyncIOMotorDatabase,
        id: str,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Updates an existing record if it exist, doesn't create if not found.

        Args:
            db:         AsyncIOMotorDatabase object.
            id:         _id of existing MongoDB record.
            db_obj:     Existing DB Object to update fields from.
            obj_in:     Pydantic Object with new data in.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_none=True)

        for field in vars(obj_in):
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        try:
            await db[self.collection].update_one(
                {"_id": ObjectId(id)},
                {"$set": db_obj.model_dump(exclude_none=True)},
            )
        except WriteError as err:
            logger.error(
                f"WriteError while attempting to update a resource ({id}) due to an error: {err}"
            )
        except OperationFailure as err:
            logger.error(
                f"OperationalFailure while attempting to update a resource in the database due to an error: {err}"
            )
            raise err
        except PyMongoError as err:
            logger.error(
                f"Caught PyMongoError while attempting to update a resource in the database due to an error: {err}"
            )
            raise err
        except Exception as err:
            logger.error(
                f"Caught unhandled exception while attempting to update resource {id} in the database due to an error: {err}"
            )

        refreshed_object = await self.get(db=db, id=id)
        return self.model.model_validate(refreshed_object)

    async def delete(self, db: AsyncIOMotorDatabase, id: str) -> int:
        """Delete a MongoDB record based on the _id, returns number of items deleted.

        Args:
            db:     AsyncIOMotorDatabase object.
            id:     _id of existing MongoDB record.
        """
        try:
            obj = await db[self.collection].delete_one({"_id": ObjectId(id)})
        except OperationFailure as err:
            logger.error(
                f"OperationalFailure while attempting to delete a resource ({id}) from the database due to an error: {err}"
            )
            raise err
        except PyMongoError as err:
            logger.error(
                f"Caught PyMongoError while attempting to delete a resource from the database due to an error: {err}"
            )
            raise err
        except Exception as err:
            logger.error(
                f"Caught unhandled exception while attempting to delete resource {id} from the database due to an error: {err}"
            )
            raise err

        return obj.deleted_count
