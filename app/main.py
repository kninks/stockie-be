import logging

from app.settings.config import config
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.common.exceptions.custom_exceptions import CustomAPIError
from app.common.middleware.logging_middleware import logging_middleware_factory
from app.common.exceptions.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    custom_api_exception_handler,
    starlette_http_exception_handler,
)
from app.settings.logging_config import setup_logging
from fastapi import FastAPI, HTTPException

from app.api.routes import test
from app.api.routes.client import predict_routes

# from starlette.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)

app = FastAPI(
    title="Stockie API",
    description="API for Stockie",
    version="1.0.0",
    debug=config.DEBUG,
    root_path="/api",
)

app.add_middleware(
    logging_middleware_factory(),
    # CORSMiddleware,
    # allow_origins=config.ALLOWED_ORIGINS, # Change this to restrict origins in production
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"],
)

app.exception_handler(StarletteHTTPException)(starlette_http_exception_handler)
app.exception_handler(Exception)(global_exception_handler)
app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(CustomAPIError)(custom_api_exception_handler)

app.include_router(predict_routes.router, prefix="/prediction", tags=["Prediction"])
app.include_router(test.router, prefix="/test", tags=["Test"])


@app.get("/", tags=["General"])
def home():
    logger.info("Home endpoint called!")
    return {"message": "Welcome to Stockie API"}
