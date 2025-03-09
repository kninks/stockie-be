# Stockie BE

## 📖 Table of Contents
- 📁 [Project Structure](#project-structure)
- 🛠 [Project Setup (Local Development)](#project-setup-local-development)
    - ⚙️ [Prerequisites](#prerequisites)
    - 📥 [Installation](#installation)
- 🚀 [Running The Server](#running-the-server)
- 🧪 [Testing](#testing)
- 👾 [Troubleshooting](#troubleshooting)
- 🤝 [Contributing](#contributing)
- 📝 [Resources](#resources)

## Project structure
```
stockie-be/
│── 📂 app                    # 🚀 Main backend application
│   │── 📂 api                # 🌍 API Layer (Controllers & Routes)
│   │   │── 📂 controllers    # 🎯 Controllers handle incoming requests
│   │   │   │── client
│   │   │   │   ├── stock_controller.py
│   │   │   │   ├── user_controller.py
│   │   │   │   ├── __init__.py
│   │   │   │── ml
│   │   │   │   ├── ml_controller.py
│   │   │   │   ├── __init__.py
│   │   │── 📂 routes         # 🚏 FastAPI Routers (Define API endpoints)
│   │   │   │── client
│   │   │   │   ├── stock_routes.py
│   │   │   │   ├── user_routes.py
│   │   │   │   ├── __init__.py
│   │   │   │── ml
│   │   │   │   ├── ml_routes.py
│   │   │   │   ├── __init__.py
│   │── 📂 core               # ⚙️ Application settings
│   │   ├── config.py         # App-wide settings (DB, API keys, etc.)
│   │   ├── database.py       # DB setup (SQLAlchemy)
│   │   ├── logging_config.py # Logging configuration
│   │   └── __init__.py
│   │── 📂 models             # 🏛 ORM models (SQLAlchemy)
│   │   │── client
│   │   │   ├── stock_model.py
│   │   │   ├── user_model.py
│   │   │   ├── __init__.py
│   │   │── ml
│   │   │   ├── ml_model.py
│   │   │   ├── __init__.py
│   │── 📂 repositories       # 💾 Database queries (Repositories)
│   │   │── client
│   │   │   ├── stock_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── __init__.py
│   │   │── ml
│   │   │   ├── ml_repository.py
│   │   │   ├── __init__.py
│   │── 📂 schemas            # 📝 Pydantic Schemas (Request/Response)
│   │   │── client
│   │   │   ├── stock_schema.py
│   │   │   ├── user_schema.py
│   │   │   ├── __init__.py
│   │   │── ml
│   │   │   ├── ml_schema.py
│   │   │   ├── __init__.py
│   │── 📂 services           # 🧠 Business logic (Service layer)
│   │   │── client
│   │   │   ├── stock_service.py
│   │   │   ├── user_service.py
│   │   │   ├── __init__.py
│   │   │── ml
│   │   │   ├── ml_service.py
│   │   │   ├── __init__.py
│   │── 📂 middleware         # 🛡 Middleware (Logging, Auth, etc.)
│   │   ├── logging_middleware.py
│   │   ├── auth_middleware.py
│   │   └── __init__.py
│   │── 📂 exceptions         # ⚠️ Custom exceptions & handlers
│   │   ├── custom_exceptions.py
│   │   ├── exception_handlers.py
│   │   └── __init__.py
│   │── 📂 utils              # 🔧 Helper utilities
│   │   ├── response_handler.py
│   │   ├── error_codes.py
│   │   ├── date_utils.py
│   │   └── __init__.py
│   │── main.py               # 🚀 FastAPI app entry point
│── 📂 tests                  # ✅ Unit & integration tests
│── .env                      # 📌 Environment variables
│── requirements.txt          # 📦 Dependencies
│── README.md                 # 📖 Project documentation
```

## Project setup (Local Development)
For first time setup of the project, follow the steps below:

### Local development
### Prerequisites
- python 3.12+
- pip (please upgrade to the latest version)
    ```bash
    python -m pip install --upgrade pip
    ```

### Installation
1. Clone the repo

2. Create a virtual environment
    ```bash
    python -m venv venv
    ```
   
3. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
   
4. Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```
   For any dependency updates, please run the following command
    ```bash
    pip freeze > requirements.txt
    ```
   
5. Install pre-commit hooks
    ```bash
    pre-commit install
    ```
   For any pre-commit hook updates, please run the following command
    ```bash
    pre-commit autoupdate
    ```
   
6. Create a `.env` file in the root directory and add the following environment variables
    ```env
    DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_6JtGrYNAxMW0@ep-long-violet-a1z2ze9p-pooler.ap-southeast-1.aws.neon.tech/neondb
    ```

You're all set! 🚀
To start the development server, follow the next section.


## Running the server

### Local development
1. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
   
2. Run the server
    ```bash
    uvicorn app.main:app --reload
    ```
   
3. To access the API documentation, visit
   - 📜 Swagger UI (interactive) → http://127.0.0.1:8000/docs
   - 🔥 ReDoc UI (read-only) → http://127.0.0.1:8000/redoc

4. To terminate the server, press `Ctrl + C` in the terminal

5. To deactivate the virtual environment, run
    ```bash
    deactivate
    ```
   
## Testing
1. To run the tests, run the following command
    ```bash
    pytest
    ```

## Troubleshooting

### Database connection
- [macOS] If you encounter the following error: 
`ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)`, 
please install the python certificates by running the following command
    ```bash
    /Applications/Python\ 3.x/Install\ Certificates.command
    ```
   Replace `3.x` with the version of python you are using.

## Contributing

1. Formatting
   - please format the code using `black` before committing
       ```bash
       black .
       ```
   - or shortcut `option + shift + f` for mac
   - or run the pre-commit hook
       ```bash
       pre-commit run --all-files
       ```


## Resources

### Database connection

- SQLalchemy →
    - https://docs.sqlalchemy.org/en/20/tutorial/index.html
    - https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Neon async → https://neon.tech/docs/guides/python#create-a-python-project

### Logging
- colorlog → https://pypi.org/project/colorlog/