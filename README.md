# Internship Application Tracker API

A FastAPI backend for tracking internship applications by company, role, status, and notes. It demonstrates REST operations, request validation, SQLite persistence, automated tests, and Git-based delivery.

## Features

- Create and list internship applications
- Update and delete applications by ID
- Validate application status values
- Preserve records in SQLite after server restarts
- Test the API without a live network connection

## Stack

- Python 3.14.9
- FastAPI 0.159.1
- Pydantic 2.14.1
- Uvicorn 0.54.0
- SQLite
- pytest 9.1.1 and HTTPX 0.28.1

## Run locally on Windows

1. Create the environment: `python -m venv .venv`
2. Activate it in Command Prompt: `.venv\Scripts\activate.bat`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`
5. Open `http://127.0.0.1:8000/docs`

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Check service health |
| POST | `/applications` | Create an application |
| GET | `/applications` | List applications |
| PUT | `/applications/{application_id}` | Replace an application |
| DELETE | `/applications/{application_id}` | Delete an application |

Valid status values are `saved`, `applied`, `interview`, `offer`, and `rejected`.

## Run tests

Run `pytest`. The test suite checks the health endpoint and an isolated SQLite create-and-list flow.

## Interview talking points

- Why an in-memory list loses data after a process restart
- How parameterized SQL separates values from query text
- How Pydantic models validate requests before database code runs
- Why tests use a temporary database instead of the development database