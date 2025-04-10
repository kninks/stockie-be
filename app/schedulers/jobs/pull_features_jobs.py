from datetime import date, datetime

from apscheduler.triggers.cron import CronTrigger

from app.core.clients.discord_client import get_discord_operations
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.core.settings.database import AsyncSessionLocal
from app.modules.internal.services.internal_service import get_internal_service
from app.modules.internal.services.job_config_service import get_job_config_service

job_config_service = get_job_config_service()
internal_service = get_internal_service()
discord = get_discord_operations()


# run inference daily
async def job_features():
    async with AsyncSessionLocal() as db:
        circuit_breaker = await job_config_service.get_job_config(
            db, JobConfigEnum.PULL_FEATURES_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.PULL_FEATURES,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return
        target_date = date.today()
        try:
            await internal_service.pull_features_all(
                db=db,
                target_date=target_date,
            )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_PULL_FEATURES,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.PULL_FEATURES,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.PULL_FEATURES,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )

    # if config.PULL_PRICES_TIME_HOUR:
    #     await discord.notify_discord_job_status(
    #         status=JobStatusEnum.SKIPPED,
    #         job_type=JobTypeEnum.PULL_PRICES,
    #         custom_message="Skip reason: circuit breaker flag.",
    #         is_critical=False,
    #         mention_everyone=False,
    #     )
    #     return
    #
    # target_date = date.today()
    #
    # try:
    #     async with AsyncSessionLocal() as db:
    #         await internal_service.pull_closing_prices_all(
    #             db=db,
    #             target_date=target_date,
    #         )
    #
    #     job_last_success[JobTypeEnum.PULL_PRICES] = datetime.now()
    #     await discord.notify_discord_job_status(
    #         status=JobStatusEnum.SUCCESS,
    #         job_type=JobTypeEnum.PULL_PRICES,
    #         is_critical=False,
    #         mention_everyone=False,
    #     )
    # except Exception as e:
    #     await discord.notify_discord_job_status(
    #         status=JobStatusEnum.FAILED,
    #         job_type=JobTypeEnum.PULL_PRICES,
    #         custom_message=str(e),
    #         is_critical=True,
    #         mention_everyone=True,
    #     )


def register_evaluation_job():
    from app.schedulers.scheduler import scheduler

    pull_hour = 19
    pull_minute = 00
    scheduler.add_job(
        job_features,
        trigger=CronTrigger(hour=pull_hour, minute=pull_minute),
        id="daily_pull_prices_job",
        name="Pull Prices Daily",
        replace_existing=True,
    )
