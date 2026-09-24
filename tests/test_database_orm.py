import pytest  # pyright: ignore[reportMissingImports]

from src.database_setup import (
    Base,
    engine,
    SessionLocal,
    ComponentHealthRecord,
    init_db,
)


@pytest.fixture(scope="function")
def db_session():
    # 1. Setup phase: Build the tables fresh in the local engine before the test runs
    init_db()
    session = SessionLocal()
    try:
        yield session  # Hand the live database transaction connection over to the test function
    finally:
        # 2. Teardown phase: Close the session and drop all tables to keep tests completely isolated
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_persist_and_read_health_record(db_session):
    # 1. Create a brand-new row instance using standard Python constructor parameters
    new_record = ComponentHealthRecord(
        component_name="api_gateway", cpu_utilization=42.5, is_healthy=True
    )

    # 2. Stage the record into the transaction log and write it permanently to the SQL file
    db_session.add(new_record)
    db_session.commit()
    db_session.refresh(
        new_record
    )  # Refreshes our object to populate its automatically generated ID

    # 3. Read the data back out using SQLAlchemy query filters
    retrieved = (
        db_session.query(ComponentHealthRecord)
        .filter_by(component_name="api_gateway")
        .first()
    )

    # 4. Assert structural boundaries and data integrity match perfectly
    assert retrieved is not None
    assert retrieved.id == 1
    assert retrieved.cpu_utilization == 42.5
    assert retrieved.is_healthy is True
