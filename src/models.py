from datetime import datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class TestRun(Base):
    __tablename__ = "test_runs"
    # Define the columns using SQLAlchemy 2.0 strict type-mapping style
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    passed_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False)

    # Automatically tracks exactly when the record is saved
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
