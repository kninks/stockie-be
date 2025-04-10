from datetime import date, datetime

from apscheduler.triggers.cron import CronTrigger

from app.core.clients.discord_client import get_discord_operations
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.core.settings.database import AsyncSessionLocal
from app.modules.internal.services.cleanup_data_service import get_cleanup_data_service
from app.modules.internal.services.job_config_service import get_job_config_service

job_config_service = get_job_config_service()
discord = get_discord_operations()
cleanup_service = get_cleanup_data_service()


async def job_cleanup_old_data():
    async with AsyncSessionLocal() as db:
        circuit_breaker = await job_config_service.get_job_config(
            db, JobConfigEnum.CLEANUP_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return
        target_date = date.today()
        trading_data_days_back = await job_config_service.get_job_config(
            db, JobConfigEnum.CLEANUP_TRADING_DATA_DAYS_BACK
        )
        predictions_days_back = await job_config_service.get_job_config(
            db, JobConfigEnum.CLEANUP_PREDICTIONS_DAYS_BACK
        )
        try:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.STARTED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message="",
                is_critical=False,
                mention_everyone=False,
            )

            await cleanup_service.clean_data(
                target_date=target_date,
                trading_data_days_back=trading_data_days_back,
                predictions_days_back=predictions_days_back,
                db=db,
            )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_INFERENCE,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.CLEANUP,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


def register_cleanup_job():
    from app.schedulers.scheduler import scheduler

    cleanup_day_of_week = "sat"
    cleanup_hour = 23
    cleanup_minute = 30
    scheduler.add_job(
        job_cleanup_old_data,
        trigger=CronTrigger(
            day_of_week=cleanup_day_of_week,
            hour=cleanup_hour,
            minute=cleanup_minute,
        ),
        id="weekly_cleanup_old_data_job",
        name="Cleanup Old Data Weekly",
        replace_existing=True,
    )
