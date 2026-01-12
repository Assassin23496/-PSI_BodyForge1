from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    func,
    Date,
)
from databases import Database

from .config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:"
    f"{settings.db_password}@{settings.db_host}:"
    f"{settings.db_port}/{settings.db_name}"
)

metadata = MetaData()

profiles = Table(
    "profiles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True, nullable=False),
    Column("password_hash", String(255), nullable=False),

    Column("name", String(100), nullable=False),
    Column("gender", String(10), nullable=False),
    Column("birth_date", Date, nullable=True),

    Column("height_cm", Float, nullable=False),
    Column("weight_kg", Float, nullable=False),
    Column("bmi", Float, nullable=False),

    Column("goal", String(20), nullable=False),
    Column("goal_months", Integer, nullable=False),

    Column("preferred_from_hour", Integer, nullable=True),
    Column("preferred_to_hour", Integer, nullable=True),

    Column("program_started_at", DateTime(timezone=True), nullable=True),
    Column("last_bmi_check_at", DateTime(timezone=True), nullable=True),

    Column("needs_bmi_update", Boolean, server_default="false"),
    Column("is_active", Boolean, server_default="true"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


bmi_records = Table(
    "bmi_records",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("profile_id", ForeignKey("profiles.id", ondelete="CASCADE")),
    Column("weight_kg", Float, nullable=False),
    Column("bmi", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

workout_plans = Table(
    "workout_plans",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("profile_id", ForeignKey("profiles.id", ondelete="CASCADE")),
    Column("goal", String(20), nullable=False),
    Column("duration_weeks", Integer, nullable=False),
    Column("plan_json", Text, nullable=False),  # prosto – trzymamy plan jako JSON (string)
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

database = Database(DATABASE_URL)
