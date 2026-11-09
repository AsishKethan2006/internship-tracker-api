import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Generator, Literal

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DATABASE = Path("applications.db")
ApplicationStatus = Literal["saved", "applied", "interview", "offer", "rejected"]


# --- Schemas ---
class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: ApplicationStatus = "saved"
    notes: str = Field(default="", max_length=500)


class ApplicationInput(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int


# --- Database setup & dependency ---
def init_db() -> None:
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('saved', 'applied', 'interview', 'offer', 'rejected')),
                notes TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    # check_same_thread=False: FastAPI may run the dependency and the endpoint
    # in different worker threads, which sqlite3 rejects by default.
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


def fetch_application(db: sqlite3.Connection, application_id: int) -> dict:
    row = db.execute(
        "SELECT id, company, role, status, notes FROM applications WHERE id = ?",
        (application_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return dict(row)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Internship Application Tracker API", lifespan=lifespan)


# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(application: ApplicationInput, db: DB):
    cursor = db.execute(
        "INSERT INTO applications (company, role, status, notes) VALUES (?, ?, ?, ?)",
        (application.company, application.role, application.status, application.notes),
    )
    db.commit()
    return {"id": cursor.lastrowid, **application.model_dump()}


@app.get("/applications", response_model=list[ApplicationResponse])
def list_applications(db: DB):
    rows = db.execute(
        "SELECT id, company, role, status, notes FROM applications"
    ).fetchall()
    return [dict(row) for row in rows]


@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: DB):
    return fetch_application(db, application_id)


@app.put("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, application: ApplicationInput, db: DB):
    fetch_application(db, application_id)  # raises 404 if missing
    db.execute(
        """
        UPDATE applications
        SET company = ?, role = ?, status = ?, notes = ?
        WHERE id = ?
        """,
        (
            application.company,
            application.role,
            application.status,
            application.notes,
            application_id,
        ),
    )
    db.commit()
    return fetch_application(db, application_id)

@app.delete("/applications/{application_id}")
def delete_application(application_id: int, db: DB):
    fetch_application(db, application_id)  # raises 404 if missing
    db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    db.commit()
    return {"message": "Application deleted"}