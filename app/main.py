import logging
from typing import cast

from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ExceptionHandler

from app.api.scheduler_jobs import scheduler_job_routes
from app.core.common.exceptions.custom_exceptions import CustomAPIError
from app.core.common.exceptions.exception_handlers import (
    custom_api_exception_handler,
    global_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler,
)
from app.core.common.middleware.logging_middleware import logging_middleware_factory
from app.core.settings.logging_config import setup_logging

# from app.core.common.middleware.role_auth_middleware import role_auth_middleware_factory


setup_logging("INFO")

from app.core.settings.config import get_config

config = get_config()

# from app.api.dummy import dummy_routes
# from app.modules.general.routes import general_routes
from app.api.internal.routes import internal_routes
from app.api.ml_ops.routes import ml_ops_routes
from app.api.public.routes import public_routes

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


app = FastAPI(
    title="Stockie BE API",
    description="API for Stockie backend server",
    version="1.0.0",
    debug=config.DEBUG,
    root_path="/api",
    # lifespan=lifespan,
)

app.add_middleware(logging_middleware_factory())
# app.add_middleware(role_auth_middleware_factory())
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    StarletteHTTPException, cast(ExceptionHandler, starlette_http_exception_handler)
)
app.add_exception_handler(Exception, cast(ExceptionHandler, global_exception_handler))
app.add_exception_handler(HTTPException, cast(ExceptionHandler, http_exception_handler))
app.add_exception_handler(
    CustomAPIError, cast(ExceptionHandler, custom_api_exception_handler)
)


app.include_router(public_routes.router)
app.include_router(scheduler_job_routes.router)
app.include_router(internal_routes.router)
app.include_router(ml_ops_routes.router)
# app.include_router(general_routes.router)
# app.include_router(dummy_routes.router)


@app.get("/", tags=["Welcome"])
def home():
    logger.info("Home endpoint called!")
    return {
        "message": "Welcome to Stockie API, please navigate to /docs for more information."
    }
