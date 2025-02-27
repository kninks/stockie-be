# Stockie BE

## Project setup (Local Development)
For first time setup of the project, follow the steps below:

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
5. Create a `.env` file in the root directory and add the following environment variables
    ```env
    ???????DATABASE_URL=sqlite:///./stockie.db
    ```

You're all set! 🚀
To start the development server, follow the next section.


## Running the server locally
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

## Notes

### Database connection
- Neon async
- https://neon.tech/docs/guides/python#create-a-python-project

