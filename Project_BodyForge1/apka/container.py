

from .db import database, metadata, DATABASE_URL
from sqlalchemy import create_engine

from .infrastructure.repositories.profile_repository_impl import ProfileRepositoryImpl
from .core.services.planning_service import PlanningService
from .core.services.bmi_service import BMIService


# Repozytoria
profile_repository = ProfileRepositoryImpl()

# Serwisy
planning_service = PlanningService(profile_repository)
bmi_service = BMIService(profile_repository, planning_service)


def create_db_engine():
    # silnik tylko do migracji / create_all
    return create_engine(DATABASE_URL.replace("+asyncpg", ""))
