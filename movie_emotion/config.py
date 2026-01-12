from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseSettingsConfig(BaseSettings):
    """Базовые настройки конфигов"""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class AdminSettings(BaseSettingsConfig):
    """Настройки админа"""

    ADMIN_USERNAME: SecretStr
    ADMIN_PASSWORD: SecretStr
    ADMIN_EMAIL: SecretStr
    DJANGO_SECRET_KEY: SecretStr
    DJANGO_DEBUG_MODE: bool = False


class PostgresSettings(BaseSettingsConfig):
    """Настройки для подключения к PostgreSQL"""

    POSTGRES_ENGINE: str = "django.db.backends.postgresql"
    POSTGRES_HOST: str
    POSTGRES_DB_NAME: str
    POSTGRES_USER: SecretStr
    POSTGRES_PASS: SecretStr
    POSTGRES_PORT: int


class EmailSettings(BaseSettingsConfig):
    """Настройки для отправки электронных писем"""

    EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST: str = "smtp.yandex.com"
    EMAIL_PORT: int = 465
    EMAIL_USE_SSL: bool = True
    EMAIL_HOST_USER: SecretStr
    EMAIL_HOST_PASSWORD: SecretStr


class Settings(BaseSettings):
    """Общий класс настроек"""

    admin: AdminSettings = AdminSettings()
    postgres: PostgresSettings = PostgresSettings()
    email: EmailSettings = EmailSettings()


env_settings = Settings()
