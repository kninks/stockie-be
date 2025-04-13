from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum
from app.modules.general.services.stock_service import StockService, get_stock_service
from app.modules.internal.services.cleanup_data_service import (
    CleanupDataService,
    get_cleanup_data_service,
)
from app.modules.internal.services.job_config_service import (
    JobConfigService,
    get_job_config_service,
)
from app.modules.internal.services.process_data_service import (
    ProcessDataService,
    get_process_data_service,
)
from app.modules.ml_ops.services.evaluation_service import (
    EvaluationService,
    get_evaluation_service,
)
from app.modules.ml_ops.services.inference_service import (
    InferenceService,
    get_inference_service,
)


class SchedulerJobService:
    def __init__(
        self,
        job_config_service: JobConfigService,
        discord_operations: DiscordOperations,
        process_data_service: ProcessDataService,
        inference_service: InferenceService,
        evaluate_service: EvaluationService,
        cleanup_data_service: CleanupDataService,
        stock_service: StockService,
    ):
        self.job_config_service = job_config_service
        self.discord = discord_operations
        self.process_data_service = process_data_service
        self.inference_service = inference_service
        self.evaluate_service = evaluate_service
        self.cleanup_data_service = cleanup_data_service
        self.stock_service = stock_service

    # ok
    async def scheduled_pull_trading_data(self, db: AsyncSession) -> None:
        circuit_breaker: bool = await self.job_config_service.get_job_config(
            db=db, key=JobConfigEnum.PULL_TRADING_DATA_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        all_stocks = await self.stock_service.get_active_ticker_values(db=db)
        today = date.today()

        try:
            await self.process_data_service.pull_trading_data(
                db=db, stock_tickers=all_stocks, target_date=today
            )

            await self.job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA,
                value=str(datetime.now()),
            )

            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )

        return None

    # ok
    async def scheduled_infer_and_save(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.SAVE_INFERENCE_PERIODS,
            JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER,
            JobConfigEnum.RUN_INFERENCE_DAYS_BACK,
            JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD,
            JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)

        circuit_breaker: bool = job_configs[JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER]
        periods: list[int] = job_configs[JobConfigEnum.SAVE_INFERENCE_PERIODS]
        days_back: int = job_configs[JobConfigEnum.RUN_INFERENCE_DAYS_BACK]
        days_forward: int = job_configs[JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD]
        last_success_pull: datetime = job_configs[
            JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA
        ]

        if circuit_breaker:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return None

        if last_success_pull < datetime.now() - timedelta(hours=6):
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message="Skip reason: pull prices job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return None

        all_stocks = await self.stock_service.get_active_ticker_values(db=db)
        tomorrow = date.today() + timedelta(days=1)

        try:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.STARTED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message="",
                is_critical=False,
                mention_everyone=False,
            )

            await self.inference_service.run_and_save_inference_by_stock_tickers(
                db=db,
                stock_tickers=all_stocks,
                target_date=tomorrow,
                days_back=days_back,
                days_forward=days_forward,
                periods=periods,
            )

            await self.job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_INFERENCE,
                value=str(datetime.now()),
            )

            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.INFERENCE,
                is_critical=False,
                mention_everyone=False,
            )

        except Exception as e:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.INFERENCE,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )

    # ok
    async def scheduled_rank_predictions(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER,
            JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD,
            JobConfigEnum.LAST_SUCCESS_INFERENCE,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)

        circuit_breaker: bool = job_configs[JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER]
        periods: list[int] = job_configs[JobConfigEnum.SAVE_INFERENCE_PERIODS]
        last_success_inference: datetime = job_configs[
            JobConfigEnum.LAST_SUCCESS_INFERENCE
        ]

        if circuit_breaker:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.RANK,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        if last_success_inference < datetime.now() - timedelta(hours=6):
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.RANK,
                custom_message="Skip reason: inference job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        industry_codes = [item for item in IndustryCodeEnum]
        tomorrow = date.today() + timedelta(days=1)

        try:
            for i in industry_codes:
                for p in periods:
                    await self.process_data_service.rank_and_save_top_prediction(
                        db=db,
                        industry_code=i,
                        period=p,
                        target_date=tomorrow,
                    )

            await self.job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_RANK,
                value=str(datetime.now()),
            )

            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.RANK,
                is_critical=False,
                mention_everyone=False,
            )

        except Exception as e:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.RANK,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )

    # ok
    async def scheduled_evaluate_accuracy(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.EVALUATE_CIRCUIT_BREAKER,
            JobConfigEnum.EVALUATE_DAYS_BACK,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)
        circuit_breaker: bool = job_configs[JobConfigEnum.EVALUATE_CIRCUIT_BREAKER]
        days_back: int = job_configs[JobConfigEnum.EVALUATE_DAYS_BACK]

        if circuit_breaker:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.EVALUATION,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        all_stocks = await self.stock_service.get_active_ticker_values(db=db)
        today = date.today()

        try:
            await self.evaluate_service.accuracy(
                db=db,
                target_date=today,
                days_back=days_back,
                stock_tickers=all_stocks,
            )

            await self.job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_EVALUATION,
                value=str(datetime.now()),
            )

            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.EVALUATION,
                is_critical=False,
                mention_everyone=False,
            )
        except Exception as e:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.EVALUATION,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )

    async def scheduled_clean_data(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.CLEANUP_CIRCUIT_BREAKER,
            JobConfigEnum.CLEANUP_TRADING_DATA_DAYS_BACK,
            JobConfigEnum.CLEANUP_PREDICTIONS_DAYS_BACK,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)
        circuit_breaker: bool = job_configs[JobConfigEnum.CLEANUP_CIRCUIT_BREAKER]
        trading_data_days_back: int = job_configs[
            JobConfigEnum.CLEANUP_TRADING_DATA_DAYS_BACK
        ]
        predictions_days_back: int = job_configs[
            JobConfigEnum.CLEANUP_PREDICTIONS_DAYS_BACK
        ]
        if circuit_breaker:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SKIPPED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        today = date.today()

        try:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.STARTED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message="",
                is_critical=False,
                mention_everyone=False,
            )

            await self.cleanup_data_service.clean_data(
                db=db,
                target_date=today,
                trading_data_days_back=trading_data_days_back,
                predictions_days_back=predictions_days_back,
            )

            await self.job_config_service.set_job_config(
                db=db,
                key=JobConfigEnum.LAST_SUCCESS_INFERENCE,
                value=str(datetime.now()),
            )

            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.SUCCESS,
                job_type=JobTypeEnum.CLEANUP,
                is_critical=False,
                mention_everyone=False,
            )

        except Exception as e:
            await self.discord.notify_discord_job_status(
                status=JobStatusEnum.FAILED,
                job_type=JobTypeEnum.CLEANUP,
                custom_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )


def get_scheduler_job_service() -> SchedulerJobService:
    return SchedulerJobService(
        job_config_service=get_job_config_service(),
        discord_operations=get_discord_operations(),
        process_data_service=get_process_data_service(),
        inference_service=get_inference_service(),
        evaluate_service=get_evaluation_service(),
        cleanup_data_service=get_cleanup_data_service(),
        stock_service=get_stock_service(),
    )


# discord = get_discord_operations()
