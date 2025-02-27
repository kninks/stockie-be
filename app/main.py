from fastapi import FastAPI
# from starlette.middleware.cors import CORSMiddleware

from app.routes import ml, test, prediction

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

app.include_router(ml.router, prefix="/ml", tags=["ML"])
app.include_router(test.router, prefix="/test", tags=["Test"])
app.include_router(prediction.router, prefix="/prediction", tags=["Prediction"])


@app.get("/", tags=["General"])
def home():
    return {"message": "Welcome to Stockie API"}

# stockie-be/
# │── app/
# │   ├── main.py
# │   ├── models.py         # Database models
# │   ├── schemas.py        # Pydantic schemas
# │   ├── database.py       # Database connection
# │   ├── services/         # Business logic
# │   ├── routes/           # API routes
# │   ├── tests/            # Unit tests
# │   ├── utils/            # Utility functions
# │── .env                  # Environment variables
# │── requirements.txt      # Dependencies
# │── README.md
# │── pyproject.toml        # For package management
# │── Dockerfile            # Docker containerization
# │── .gitignore            # Git ignore file

# app/
# ├── database.py         # Handles DB connection
# ├── main.py             # FastAPI app entry point
# ├── models.py           # SQLAlchemy models (optional)
# ├── schemas.py          # Pydantic schemas for request/response validation
# ├── repositories/       # Repository layer (Handles DB queries)
# │   ├── test_repository.py
# │   ├── user_repository.py
# ├── services/           # Business logic layer (optional)
# │   ├── test_service.py
# │   ├── user_service.py
# ├── routes/             # API endpoints (Controllers)
# │   ├── test.py
# │   ├── user.py
# ├── queries/            # Raw SQL files (if applicable)
# │   ├── test_queries.sql
# │   ├── user_queries.sql
