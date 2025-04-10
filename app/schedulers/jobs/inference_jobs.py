from datetime import date, datetime, timedelta

from apscheduler.triggers.cron import CronTrigger

from app.core.clients.discord_client import get_discord_operations
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.core.settings.database import AsyncSessionLocal
from app.modules.internal.services.internal_service import get_internal_service
from app.modules.internal.services.job_config_service import get_job_config_service
from app.modules.ml_ops.services.inference_service import get_inference_service

job_config_service = get_job_config_service()
inference_service = get_inference_service()
internal_service = get_internal_service()
discord = get_discord_operations()


# run inference daily
async def job_run_and_save_inference():
    async with AsyncSessionLocal() as db:
        configs = await job_config_service.get_job_configs(
            db,
            [
                JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER,
                JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA,
                JobConfigEnum.RUN_INFERENCE_DAYS_BACK,
                JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD,
            ],
        )
        circuit_breaker = bool(configs[JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER])
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        if configs[JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA] < datetime.now() - timedelta(hours=6):
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message="Skip reason: pull prices job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        target_date = date.today() + timedelta(days=1)
        days_back = configs[JobConfigEnum.RUN_INFERENCE_DAYS_BACK]
        days_forward = configs[JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD]
        save_inference_periods = configs[JobConfigEnum.SAVE_INFERENCE_PERIODS]

        await discord.notify_discord_job_status(
            status=JobStatusEnum.STARTED,
            job_type=JobTypeEnum.INFERENCE,
            custom_message="",
            is_critical=False,
            mention_everyone=False,
        )

        try:
            await inference_service.run_and_save_inference_all(
                db=db,
                target_date=target_date,
                days_back=days_back,
                days_forward=days_forward,
                periods=save_inference_periods,
            )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_INFERENCE,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.INFERENCE,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


async def job_rank_predictions():
    async with AsyncSessionLocal() as db:
        configs = await job_config_service.get_job_configs(
            db,
            [
                JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER,
                JobConfigEnum.LAST_SUCCESS_INFERENCE,
                JobConfigEnum.SAVE_INFERENCE_PERIODS,
            ],
        )
        circuit_breaker = configs[JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER]
        if circuit_breaker:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.RANK,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        if configs[JobConfigEnum.LAST_SUCCESS_INFERENCE] < datetime.now() - timedelta(hours=6):
            await discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.RANK,
                custom_message="Skip reason: inference job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        target_date = date.today() + timedelta(days=1)
        periods = configs[JobConfigEnum.SAVE_INFERENCE_PERIODS]

        try:
            for period in periods:
                await internal_service.rank_and_save_top_predictions_all(
                    db=db,
                    target_date=target_date,
                    period=period,
                )

            await job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_RANK,
                value=str(datetime.now()),
            )

            await discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.RANK,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.RANK,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


def register_inference_job():
    from app.schedulers.scheduler import scheduler

    run_inference_hour = 21
    run_inference_minute = 00
    scheduler.add_job(
        job_run_and_save_inference,
        trigger=CronTrigger(
            hour=run_inference_hour,
            minute=run_inference_minute,
        ),
        id="daily_inference_job",
        name="Run Inference Daily",
        replace_existing=True,
    )

    rank_hour = 22
    rank_minute = 00
    scheduler.add_job(
        job_rank_predictions,
        trigger=CronTrigger(
            hour=rank_hour,
            minute=rank_minute,
        ),
        id="daily_rank_job",
        name="Rank Predictions Daily",
        replace_existing=True,
    )
