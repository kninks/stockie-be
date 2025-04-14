
# Stockie BE

## 📖 Table of Contents
- 🛠 [Project Setup (Local Development)](#project-setup-local-development)
    - ⚙️ [Prerequisites](#prerequisites)
    - 📥 [Installation](#installation)
- 🚀 [Running The Server](#running-the-server)
- 🧪 [Testing](#testing)
- 👾 [Troubleshooting](#troubleshooting)
- 🤝 [Contributing](#contributing)
- 📝 [Resources](#resources)

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
   
4. Install the libraries
    ```bash
    pip install -r requirements.txt
    ```
   For any libraries updates, please run the following command
    ```bash
    pip freeze > requirements.txt
    ```

5. Create a `.env` file in the root directory and add the environment variables (please ask for the variables from the team)

6. If you are working with scheduler, currently we are using terraform to deploy the scheduler to google cloud scheduler
   - Please make sure you have the following installed
     - [Terraform](https://www.terraform.io/downloads.html)
     - login to gcloud with the permitted account

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
    uvicorn app.main:app --port 8000 --reload
    ```
   or run with the main file (no real-time reload)
   ```bash
   python -m app.main
   ```
   
3. To access the API documentation, visit
   - 📜 Swagger UI (interactive) → http://127industry_code.0.0.1:8000/docs
     - API KEY are needed in order to call any endpoints
     - This server's API KEY allows access to every endpoint
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

### Running docker locally

For this repo, mostly you will want to compose up the docker only when you want to test the scheduler or job config

- Prerequisite: Make sure you have Docker/Orb stack installed and running
    - [Docker Desktop](https://www.docker.com/products/docker-desktop)
    - [Docker CLI](https://docs.docker.com/engine/install/)
    - [Docker Compose](https://docs.docker.com/compose/install/)

1. Pull the img
2. Compose up docker dev if you have never built the image or no changes are made to the Dockerfile (no need to run in python venv).

   If you have already built the docker image, and no changes are made to the Dockerfile, you can skip the build step
    ```bash
    docker-compose -f docker-compose.dev.yml up --build
    ```
   simulate prod env
    ```bash
    docker-compose -f docker-compose.prod.yml up --build
    ```
3. Compose up docker dev if you have already built the image and no changes are made to the Dockerfile
    ```bash
    docker-compose -f docker-compose.dev.yml up
    ```
   simulate prod env
    ```bash
    docker-compose -f docker-compose.prod.yml up
    ```
4. compose down
    ```bash
    docker-compose -f docker-compose.dev.yml down
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

### Formatting
- please format the code by running the pre-commit hook before committing
    ```bash
    pre-commit run --all-files
    ```
  or
    ```bash
    black app/
    isort app/
    flake8 app/
    ```
  or shortcut `option + shift + f` for mac 
- For any pre-commit hook updates, please run the following command
     ```bash
     pre-commit autoupdate
     ```

### Database Migrations (with Alembic)
This project uses Alembic to handle database schema migrations
- Please ensure that the Alembic database URL is set in the `.env` file
- To create a new migration, run the following command
    ```bash
    alembic revision --autogenerate -m "migration message"
    ```
- To apply the migrations, run
    ```bash
    alembic upgrade head
    ```

### Scheduler
- To schedule a job, please go to `/infra` and add the job to the `scheduler.tf` file
- To deploy the scheduler, run the following command
    ```bash
    terraform init        # Only once per setup or if providers/backend changes
    terraform fmt         # (Optional) Format files nicely
    terraform validate    # (Optional) Check for syntax issues
    terraform plan        # See what changes will happen
    terraform apply       # Actually apply the changes
    ```

## Resources

### Database connection

- SQLalchemy →
    - https://docs.sqlalchemy.org/en/20/tutorial/index.html
    - https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Neon async → https://neon.tech/docs/guides/python#create-a-python-project

### Logging
- colorlog → https://pypi.org/project/colorlog/

### Alembic
- Alembic → https://alembic.sqlalchemy.org/en/latest/index.html

## Notes

### Dependency Injection (DI)
- _**Constructor Injection**_ : complex dependencies or manage more state and logic (like services).
- _**Static Methods with DI**_ : simple logic that just need to delegate to another layer without managing any state themselves.


#### Summary for this project
- top-prediction endpoints
    - _**route layer**_ : Static Methods with DI for db session and auth (not for controllers)
    - _**controller layer**_ : Static Methods with DI for services
    - _**service layer**_ : Constructor Injection for repositories

- ml-ops endpoints
    - _**route layer**_ : Static Methods with DI for db session and auth (not for controllers)
    - _**controller layer**_ : Static Methods with DI for services
    - _**service layer**_ : Constructor Injection for repositories and ml client