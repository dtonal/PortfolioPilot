# PortofolioPilot - Your Personal Stock Tracking and Analysis Tool

## Overview

AktienApp is a personal web application designed to help you track and analyze stock market data and manage a virtual stock portfolio. It allows you to monitor real-time and historical stock prices, add virtual stock holdings with purchase details, and analyze the performance of your simulated investments over time.
The main goal for this project is to learn some (for me) new framework in python.
## Technology Stack

This project utilizes the following technologies:

* **Backend (API):** Python
    * **Web Framework:** Flask (initially chosen for its simplicity and ease of learning)
    * **Database Interaction:** SQLAlchemy (for object-relational mapping and database interaction)
    * **Data Format:** JSON (for communication between the backend API and the frontend)
    * **Logging:** Python's built-in `logging` library for application logging.
* **Frontend (User Interface):** Vue.js (a progressive JavaScript framework for building dynamic and interactive web UIs).
* **Database:** SQLite (initially chosen for its file-based simplicity and suitability for smaller projects).
* **Project Management & Packaging:** Poetry (for managing dependencies, project structure, and building the application).
* **Version Control:** Git with GitHub.
* **Testing:** pytest for writing and running unit tests.
* **Deployment (Future):** Cloud Platform (for hosting the application).

## Getting Started (Initial Setup)

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd aktienapp
    ```

2.  **Install Poetry:**
    If you haven't already, install Poetry following the instructions on the official website: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

3.  **Create and activate the virtual environment using Poetry:**
    ```bash
    poetry install
    poetry shell
    ```
    This command will create a virtual environment and install all the project dependencies listed in `pyproject.toml` and locked in `poetry.lock`. The `poetry shell` command will then activate this environment.

4.  **(Optional) Set up the database:**
    For the initial SQLite setup, SQLAlchemy will likely handle the creation of the database file when the application is run for the first time or when database models are defined and created. Further database migrations might be needed as the project evolves (consider using Alembic with SQLAlchemy later).

5.  **Run the backend API (example - adjust based on your actual API entry point):**
    ```bash
    poetry run python aktienapp/main.py
    ```
    (You will need to create `aktienapp/main.py` with your Flask application logic.)

6.  **Set up and run the frontend (assuming a standard Vue.js setup):**
    Navigate to the frontend directory (if you structure your project with a separate `frontend` folder):
    ```bash
    cd frontend
    npm install  # or yarn install
    npm run serve # or yarn serve
    ```
    (You will need to set up your Vue.js project separately, potentially using the Vue CLI.)

## Next Steps

* Start building the backend API using Flask to handle user registration/login, stock data fetching, and portfolio management.
* Define the database models using SQLAlchemy to interact with the SQLite database.
* Begin developing the frontend with Vue.js to create the user interface for viewing stock data and managing portfolios.
* Implement API endpoints for the frontend to consume.
* Write unit tests using pytest to ensure the reliability of your backend logic.
