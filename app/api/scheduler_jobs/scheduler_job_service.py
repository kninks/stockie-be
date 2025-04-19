import logging
from asyncio import gather
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.internal.services.cleanup_data_service import (
    CleanupDataService,
    get_cleanup_data_service,
)
from app.api.internal.services.job_config_service import (
    JobConfigService,
    get_job_config_service,
)
from app.api.internal.services.process_data_service import (
    ProcessDataService,
    get_process_data_service,
)
from app.api.ml_ops.services.inference_service import (
    InferenceService,
    get_inference_service,
)
from app.core.clients.discord_client import DiscordOperations, get_discord_operations
from app.core.common.utils.datetime_utils import (
    get_today_bangkok_date,
    is_market_closed,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.job_enum import JobConfigEnum, JobStatusEnum, JobTypeEnum

logger = logging.getLogger(__name__)


class SchedulerJobService:
    def __init__(
        self,
        job_config_service: JobConfigService,
        discord_operations: DiscordOperations,
        process_data_service: ProcessDataService,
        inference_service: InferenceService,
        cleanup_data_service: CleanupDataService,
        stock_service: StockService,
    ):
        self.job_config_service = job_config_service
        self.discord = discord_operations
        self.process_data_service = process_data_service
        self.inference_service = inference_service
        self.cleanup_data_service = cleanup_data_service
        self.stock_service = stock_service

    async def _handle_job_executed(
        self,
        db: AsyncSession,
        job_type: JobTypeEnum,
        job_status: JobStatusEnum,
        is_critical: bool,
        mention_everyone: bool,
        additional_message: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ):
        if job_status == JobStatusEnum.FAILED:
            logger_func = logger.critical
            success_value = "false"
        elif job_status in {JobStatusEnum.SKIPPED, JobStatusEnum.WARNING}:
            logger_func = logger.warning
            success_value = "false"
        else:
            logger_func = logger.info
            success_value = "true"

        if job_type == JobTypeEnum.PULL_TRADING_DATA:
            job_success_value = JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA
        elif job_type == JobTypeEnum.RANK:
            job_success_value = JobConfigEnum.LAST_SUCCESS_RANK
        elif job_type == JobTypeEnum.EVALUATION:
            job_success_value = JobConfigEnum.LAST_SUCCESS_EVALUATION
        elif job_type == JobTypeEnum.CLEANUP:
            job_success_value = JobConfigEnum.LAST_SUCCESS_CLEANUP
        elif job_type == JobTypeEnum.INFERENCE:
            job_success_value = JobConfigEnum.LAST_SUCCESS_INFERENCE
        else:
            raise ValueError(f"Unknown job type: {job_type}")

        tag_str = " ".join(f"[{tag}]" for tag in tags) if tags else ""
        message = f"{job_status.value} {tag_str}".strip()

        if additional_message:
            message += f" — {additional_message}"

        logger_func(f"[{job_type.value}] {message}")

        await self.job_config_service.set_job_config(
            db=db,
            key=job_success_value,
            value=success_value,
        )

        await self.discord.send_discord_message(
            job_name=job_type.value,
            message=additional_message,
            is_critical=is_critical,
            mention_everyone=mention_everyone,
        )

    async def scheduled_pull_trading_data(self, db: AsyncSession) -> None:
        circuit_breaker: bool = await self.job_config_service.get_job_config(
            db=db, key=JobConfigEnum.PULL_TRADING_DATA_CIRCUIT_BREAKER
        )
        if circuit_breaker:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
                tags=["pull"],
            )
            return

        today = get_today_bangkok_date()

        if is_market_closed(today):
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: market close date.",
                is_critical=False,
                mention_everyone=False,
                tags=["pull"],
            )
            return

        all_stocks = await self.stock_service.get_active_ticker_values(db=db)

        try:
            failed_trading_data = await self.process_data_service.pull_trading_data(
                db=db, stock_tickers=all_stocks, target_date=today
            )

            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                job_status=JobStatusEnum.SUCCESS,
                additional_message=f"Failed tickers: {failed_trading_data}",
                is_critical=False,
                mention_everyone=False,
            )
            return None
        except Exception as e:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.PULL_TRADING_DATA,
                job_status=JobStatusEnum.FAILED,
                additional_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )
            raise e

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
        print("periods", periods)
        days_back: int = job_configs[JobConfigEnum.RUN_INFERENCE_DAYS_BACK]
        days_forward: int = job_configs[JobConfigEnum.RUN_INFERENCE_DAYS_FORWARD]
        last_success_pull: bool = job_configs[
            JobConfigEnum.LAST_SUCCESS_PULL_TRADING_DATA
        ]

        if circuit_breaker:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.INFERENCE,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return None

        if not last_success_pull:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.INFERENCE,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: pull prices job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return None

        today = get_today_bangkok_date()
        all_industry_codes = [item for item in IndustryCodeEnum]

        try:
            tasks = [
                self.inference_service.run_and_save_inference_by_industry_code(
                    db=db,
                    industry_code=industry_code,
                    target_date=today,
                    days_back=days_back,
                    days_forward=days_forward,
                    periods=periods,
                )
                for industry_code in all_industry_codes
            ]

            results = await gather(*tasks, return_exceptions=True)

            if not results:
                raise

            failed_industries = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_industries.append((all_industry_codes[i].value, str(result)))

            if failed_industries:
                error_msg = "\n".join(
                    [f"{industry}: {error}" for industry, error in failed_industries]
                )
                await self._handle_job_executed(
                    db=db,
                    job_type=JobTypeEnum.INFERENCE,
                    job_status=JobStatusEnum.FAILED,
                    additional_message=f"Some industries failed:\n{error_msg}",
                    is_critical=True,
                    mention_everyone=True,
                )
            else:
                await self._handle_job_executed(
                    db=db,
                    job_type=JobTypeEnum.INFERENCE,
                    job_status=JobStatusEnum.SUCCESS,
                    is_critical=False,
                    mention_everyone=False,
                )

            return

        except Exception as e:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.INFERENCE,
                job_status=JobStatusEnum.FAILED,
                additional_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )
            raise e

    # ok
    async def scheduled_rank_predictions(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER,
            JobConfigEnum.SAVE_INFERENCE_PERIODS,
            JobConfigEnum.LAST_SUCCESS_INFERENCE,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)

        circuit_breaker: bool = job_configs[JobConfigEnum.RUN_INFERENCE_CIRCUIT_BREAKER]
        periods: list[int] = job_configs[JobConfigEnum.SAVE_INFERENCE_PERIODS]
        last_success_inference: bool = job_configs[JobConfigEnum.LAST_SUCCESS_INFERENCE]

        if circuit_breaker:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.RANK,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        if not last_success_inference:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.RANK,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: inference job not run.",
                is_critical=False,
                mention_everyone=True,
            )
            return

        industry_codes = [item for item in IndustryCodeEnum]
        today = get_today_bangkok_date()

        try:
            result = await self.process_data_service.rank_and_save_top_predictions(
                db=db,
                industry_codes=industry_codes,
                periods=periods,
                target_dates=[today],
            )

            failed_tasks = result["failed"]
            if len(failed_tasks) != 0:
                error_msg = "\n".join(
                    [
                        f"Industry: {i}, Period: {p}, Date: {d}"
                        for i, p, d, msg in failed_tasks
                    ]
                )
                await self._handle_job_executed(
                    db=db,
                    job_type=JobTypeEnum.RANK,
                    job_status=JobStatusEnum.FAILED,
                    additional_message=f"Some rankings failed:\n{error_msg}",
                    is_critical=True,
                    mention_everyone=True,
                )
                raise Exception("Ranking job failed for some industries/periods.")

            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.RANK,
                job_status=JobStatusEnum.SUCCESS,
                is_critical=False,
                mention_everyone=False,
            )
            return
        except Exception as e:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.RANK,
                job_status=JobStatusEnum.FAILED,
                additional_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )
            raise e

    async def scheduled_evaluate_accuracy(self, db: AsyncSession) -> None:
        keys = [
            JobConfigEnum.EVALUATE_CIRCUIT_BREAKER,
            JobConfigEnum.EVALUATE_DAYS_BACK,
        ]
        job_configs = await self.job_config_service.get_job_configs(db=db, keys=keys)
        circuit_breaker: bool = job_configs[JobConfigEnum.EVALUATE_CIRCUIT_BREAKER]
        days_back: int = job_configs[JobConfigEnum.EVALUATE_DAYS_BACK]

        if circuit_breaker:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.EVALUATION,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        all_stocks = await self.stock_service.get_active_ticker_values(db=db)
        today = get_today_bangkok_date()

        try:
            await self.process_data_service.accuracy(
                db=db,
                target_date=today,
                days_back=days_back,
                stock_tickers=all_stocks,
            )

            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.EVALUATION,
                job_status=JobStatusEnum.SUCCESS,
                is_critical=False,
                mention_everyone=False,
            )
            return
        except Exception as e:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.EVALUATION,
                job_status=JobStatusEnum.FAILED,
                additional_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )
            raise e

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
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.CLEANUP,
                job_status=JobStatusEnum.SKIPPED,
                additional_message="Skip reason: circuit breaker flag.",
                is_critical=False,
                mention_everyone=False,
            )
            return

        today = get_today_bangkok_date()

        try:
            await self.cleanup_data_service.clean_data(
                db=db,
                target_date=today,
                trading_data_days_back=trading_data_days_back,
                predictions_days_back=predictions_days_back,
            )

            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.CLEANUP,
                job_status=JobStatusEnum.SUCCESS,
                is_critical=False,
                mention_everyone=False,
            )
            return

        except Exception as e:
            await self._handle_job_executed(
                db=db,
                job_type=JobTypeEnum.CLEANUP,
                job_status=JobStatusEnum.FAILED,
                additional_message=str(e),
                is_critical=True,
                mention_everyone=True,
            )
            raise e


def get_scheduler_job_service() -> SchedulerJobService:
    return SchedulerJobService(
        job_config_service=get_job_config_service(),
        discord_operations=get_discord_operations(),
        process_data_service=get_process_data_service(),
        inference_service=get_inference_service(),
        cleanup_data_service=get_cleanup_data_service(),
        stock_service=get_stock_service(),
    )
