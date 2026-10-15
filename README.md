# Expense Management System
This project is an expense management system built with Python, MySQL, a FastAPI backend server, and a Streamlit frontend web application.

## Project Structure
- **fronted/**: Streamlit web application (`app.py`, `add_update_ui.py`, `analytics_ui.py`, `analtics_month.py`).
- **backend/**: FastAPI REST API (`server_check.py`, `db_helper.py`, `logging_setup.py`).
- **test/**: Pytest test suite for backend and database operations.
- **requirements.txt**: Required Python dependencies.
- **README.md**: Project overview and instructions.

## Setup Instructions

1. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Configure MySQL Database**:
    Ensure MySQL is running on `localhost:3306` with database `expense_manager` and user credentials configured in `backend/db_helper.py`.

3. **Run the FastAPI server**:
    From the project root:
    ```bash
    python -m uvicorn backend.server_check:app --reload
    ```
    Or from within `backend/`:
    ```bash
    uvicorn server_check:app --reload
    ```
    API documentation is accessible at: `http://localhost:8000/docs`

4. **Run the Streamlit app**:
    From the project root:
    ```bash
    streamlit run fronted/app.py
    ```
    The web interface will open at: `http://localhost:8501`

5. **Deploy to Streamlit Community Cloud**:
    - Repository: `rschaurasiya/Expense_management`
    - Branch: `main`
    - Main file path: `fronted/app.py`

6. **Run tests**:
    ```bash
    pytest
    ```