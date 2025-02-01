# Stockie BE

## Running the server
1. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
2. Run the server locally
    ```bash
    uvicorn app.main:app --reload
    ```
3. To access the API documentation, visit
   - 📜 Swagger UI (interactive) → http://127.0.0.1:8000/docs
   - 🔥 ReDoc UI (read-only) → http://127.0.0.1:8000/redoc

## Project setup

### Prerequisites
- python 3.12+
- pip (please upgrade to the latest version)
    ```bash
    python -m pip install --upgrade pip
    ```

### Installation (First time setup)
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
6. Run the server
    ```bash
    uvicorn app.main:app --reload
    ```
   

