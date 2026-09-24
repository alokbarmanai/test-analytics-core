from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean

from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Define the local file-based database engine pointer
DATABASE_URL = "sqlite:///./component_metrics.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. Establish the Base model mapper class
Base = declarative_base()

# 3. Create the Session factory layer
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 4. Construct the physical Relational Table Schema Definition
class ComponentHealthRecord(Base):
    __tablename__ = "component_health"  # The name of the table in SQL

    id = Column(Integer, primary_key=True, index=True)
    component_name = Column(String, nullable=False)
    cpu_utilization = Column(Float, default=0.0)
    is_healthy = Column(Boolean, default=True)


def init_db():
    # Automatically scan all classes inheriting from Base and build the physical SQL tables
    Base.metadata.create_all(bind=engine)
