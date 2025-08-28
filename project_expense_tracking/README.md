# Expense Management System
This project is an expense management system that consists of PYTHON PROGRAMMING, MYSQL DATABASE SERVER, A STREAMLIT FRONTED APPLICATION  and A FastAPI backend server.


## Project Structure
- **fronted/**: Contains the streamlit application code.
- **backend/**: Contain the FastAPI backend server code.
- **test/**: Contain the test for both fronted and backend.
- **requirement/**:List the required Python package.
- **README.md/**: Provides an overview and instruction for the project.

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/rschaurasiya/expense-management
    cd expense-management-system
    ```
2. **Install dependencies**:
    ```commandline
    pip install -r requirements.txt
    ```
3. **Run the FastAPI server**:
    ```commandline
   uvicorn server_check:app --reload
    ```
4. **Run the Sreamlit app**:
    ```commandline
    streamlit run fronted/app.py

    ```
