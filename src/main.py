from typing import Any, Dict, Generator, List

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import Base, SessionLocal, engine
from src.models import TestRun
from src.parser import calculate_metrics

Base.metadata.create_all(
    bind=engine
)  # Create tables in the database if they don't exist


class TestCase(BaseModel):
    name: str
    status: str
    retries: int


app = FastAPI(title="Test Analytics Service")


# 2. Add the return type annotation here
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Test Analytics Service is running successfully.",
    }


@app.post("/analytics")
async def create_analytics(
    payload: List[TestCase], db: Session = Depends(get_db)
) -> dict[str, Any]:

    # Convert the Pydantic objects back to a list of dicts for your calculator
    raw_payload = [item.model_dump() for item in payload]

    # 1. Compute metrics first
    metrics = calculate_metrics(raw_payload)

    # 2. Build the database entry using your custom models
    db_run = TestRun(
        total_tests=metrics["total"],
        passed_tests=metrics["passed"],
        failed_tests=metrics["failed"],
        pass_rate=metrics["pass_rate_percentage"],
    )

    # 3. Commit the transaction permanently to test_analytics.db
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    # 4. Return the resulting dictionary to the user
    return metrics


@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    # This queries your database and fetches every row inside the analytics table
    results = db.query(TestRun).all()
    return results


# Import your TestRun model along with your existing route models
@app.get("/history")
async def get_history(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    # 1. Query all saved rows from the test_runs table
    runs = db.query(TestRun).all()

    # 2. Format the database model rows into clean dictionaries for the API response
    history_summary = [
        {
            "id": run.id,
            "total_tests": run.total_tests,
            "passed_tests": run.passed_tests,
            "failed_tests": run.failed_tests,
            "pass_rate": run.pass_rate,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }
        for run in runs
    ]

    return history_summary


@app.delete("/analytics/{run_id}")
async def delete_analytics(
    run_id: int, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Remove a single specific test execution run record by its unique database ID."""
    # 1. Query the specific test run by its ID
    run = db.query(TestRun).filter(TestRun.id == run_id).first()

    # 2. If the test run doesn't exist, return an error
    if not run:
        return {"error": f"Test run with ID {run_id} not found"}

    # 3. Delete the test run from the database
    db.delete(run)
    db.commit()

    # 4. Return a success message
    return {
        "message": f"Test run with ID {run_id} deleted successfully",
        "deleted_id": run_id,
    }


# @app.delete("/analytics/reset")
# def reset_analytics_data(db: Session = Depends(get_db)) -> dict[str, str]:
#     """Wipe all execution records from the test_runs table to start fresh."""
#     try:
#         # This deletes every row inside the TestRun table at once
#         deleted_rows = db.query(TestRun).delete()
#         db.commit()
#         return {
#             "status": "success",
#             "message": f"Database reset completed successfully. Removed {deleted_rows} records."
#         }
#     except Exception as e:
#         db.rollback()
#         return {
#             "status": "error",
#             "message": f"Failed to reset database: {str(e)}"
#         }
