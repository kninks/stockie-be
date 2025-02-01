from fastapi import FastAPI

app = FastAPI(
    title="Stockie API",
    description="API for Stockie",
    version="1.0.0",
)

@app.get("/")
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
# │── .env                  # Environment variables
# │── requirements.txt      # Dependencies
# │── README.md
# │── pyproject.toml        # For package management
# │── Dockerfile            # Docker containerization
# │── .gitignore            # Git ignore file