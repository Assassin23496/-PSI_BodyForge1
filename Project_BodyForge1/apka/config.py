from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bodyforge"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # ile tygodni ma trwać domyślny plan
    default_plan_weeks: int = 8

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()
