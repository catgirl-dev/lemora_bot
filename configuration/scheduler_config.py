from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

def create_scheduler() -> AsyncIOScheduler:
    return AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(
            url='sqlite:///userdata.db'
        )
    }
)
