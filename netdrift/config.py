from pydantic_settings import BaseSettings
from pydantic import MongoDsn, RedisDsn


class Settings(BaseSettings):
    # API Token key to search in HTTP Headers
    API_TOKEN_KEY: str = "x-api-key"

    # API Token to use for authentication
    API_TOKEN: str = "change-me-please"

    # MongoDB URI
    MONGO_URI: MongoDsn = "mongodb://root:example@localhost:27017"

    # MongoDB default database
    MONGO_DB: str = "netdrift"

    # Redis Worker Configuration
    REDIS_HOST: RedisDsn = "redis://localhost"


settings = Settings()
