import logging

from app.utils.logging_config import setup_logging
from fastapi import FastAPI

from app.routes import prediction, test

# from starlette.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stockie API",
    description="API for Stockie",
    version="1.0.0",
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change this to restrict origins in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(prediction.router, prefix="/prediction", tags=["Prediction"])
app.include_router(test.router, prefix="/test", tags=["Test"])


@app.get("/", tags=["General"])
def home():
    logger.info("Home endpoint called!")
    return {"message": "Welcome to Stockie API"}
