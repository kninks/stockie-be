from datetime import date, datetime

from apscheduler.triggers.cron import CronTrigger

from app.core.clients.discord_client import get_discord_operations
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.core.settings.database import AsyncSessionLocal
from app.modules.internal.services.job_config_service import get_job_config_service
from app.modules.internal.services.process_data_service import get_process_data_service

job_config_service = get_job_config_service()
internal_service = get_process_data_service()
discord = get_discord_operations()


# OK
# run inference daily
async def job_trading_data():
    async with AsyncSessionLocal() as db:
        circuit_breaker = await job_config_service.get_job_config(
            db, JobConfigEnum.PULL_TRADING_DATA_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return
        target_date = date.today()
        try:
            await internal_service.pull_trading_data_all(
                db=db,
                target_date=target_date,
            )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


def register_evaluation_job():
    from app.schedulers.scheduler import scheduler

    pull_hour = 19
    pull_minute = 00
    scheduler.add_job(
        job_trading_data,
        trigger=CronTrigger(hour=pull_hour, minute=pull_minute),
        id="daily_pull_trading_data_job",
        name="Pull Trading Data Daily",
        replace_existing=True,
    )
