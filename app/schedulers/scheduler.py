import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def start_scheduler():
    try:
        scheduler.start()
        logger.info("✅ APScheduler started")
    except Exception as e:
        logger.exception("Failed to start scheduler")
        raise e
