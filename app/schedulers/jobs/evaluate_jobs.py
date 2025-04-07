from datetime import date, datetime

from apscheduler.triggers.cron import CronTrigger

from app.core.clients.discord_client import get_discord_operations
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.core.settings.database import AsyncSessionLocal
from app.modules.internal.services.job_config_service import get_job_config_service
from app.modules.ml_ops.services.evaluation_service import get_evaluation_service

job_config_service = get_job_config_service()
evaluate_service = get_evaluation_service()
discord = get_discord_operations()


# run inference daily
async def job_evaluate_accuracy():
    async with AsyncSessionLocal() as db:
        circuit_breaker = await job_config_service.get_job_config(
            db, JobConfigEnum.EVALUATE_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.EVALUATION,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return
        target_date = date.today()
        days_back = await job_config_service.get_job_config(
            db, JobConfigEnum.EVALUATE_DAYS_BACK
        )
        try:
            await evaluate_service.accuracy_all(
                db=db,
                target_date=target_date,
                days_back=days_back,
            )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_EVALUATION,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.EVALUATION,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.EVALUATION,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


def register_evaluation_job():
    from app.schedulers.scheduler import scheduler

    evaluate_hour = 2
    evaluate_minute = 45
    scheduler.add_job(
        job_evaluate_accuracy,
        trigger=CronTrigger(hour=evaluate_hour, minute=evaluate_minute),
        id="daily_evaluate_job",
        name="Evaluate Accuracy Daily",
        replace_existing=True,
    )
