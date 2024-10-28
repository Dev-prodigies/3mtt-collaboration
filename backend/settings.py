from typing import Union
from pydantic import EmailStr, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsConf:
    model_config = SettingsConfigDict(
        env_file='./.env',
        env_file_encoding='utf-8',
        extra="allow"
    )

class DbSettings(BaseSettings, SettingsConf):
    DB_USER: str = "myuser"
    DB_PASSWORD: str ="mypassword"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "mydatabase"
    # TODO: auto generate DB_URL
    DB_URL: Union[None, PostgresDsn] =  None

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        if v is None:
            return f"postgresql+asyncpg://{values['DB_USER']}:{values['DB_PASSWORD']}@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        return v

class RedisSettings(BaseSettings, SettingsConf):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

class MailSettings(BaseSettings, SettingsConf):
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str

class Secret(BaseSettings, SettingsConf):
    SECRET_KEY: str
