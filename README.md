# Stockie BE

## 📖 Table of Contents
- 📁 [Project Structure](#project-structure)
- 🛠 [Project Setup (Local Development)](#project-setup-local-development)
    - ⚙️ [Prerequisites](#prerequisites)
    - 📥 [Installation](#installation)
- 🚀 [Running The Server](#running-the-server)
- 🧪 [Testing](#testing)
- 👾 [Troubleshooting](#troubleshooting)
- 📝 [Resources](#resources)

## Project structure
```
stockie-be/
│── app/
│   ├── main.py
│   ├── models/         # Database models
│   ├── services/         # Business logic
│   ├── routes/           # API routes
│   ├── tests/            # Unit tests
│   ├── utils/            # Utility functions
│── .env                  # Environment variables
│── requirements.txt      # Dependencies
│── README.md
│── pyproject.toml        # For package management
│── Dockerfile            # Docker containerization
│── .gitignore            # Git ignore file
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