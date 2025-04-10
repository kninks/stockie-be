import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.schedulers.jobs.cleanup_jobs import register_cleanup_job
from app.schedulers.jobs.evaluate_jobs import register_evaluation_job
from app.schedulers.jobs.inference_jobs import register_inference_job

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def start_scheduler():
    try:
        scheduler.start()
        logger.info("APScheduler started")
    except Exception as e:
        logger.exception("Failed to start scheduler")
        raise e


def register_all_jobs():
    register_inference_job()
    register_evaluation_job()
    register_cleanup_job()