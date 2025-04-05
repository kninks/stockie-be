import logging

from app.modules.ml_ops.services.inference_service import InferenceService

logger = logging.getLogger(__name__)


# run inference daily
async def job_run_and_save_inference():
    """
    Run and save inference daily
    """
    logger.info("[Scheduler] Starting scheduled inference job")
    inference_service = InferenceService()
    await inference_service.run_inference_by_stock_tickers()
