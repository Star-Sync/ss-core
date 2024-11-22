from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://starsync:starsync@ss-db:5432/starsync"
)

engine = create_engine(DATABASE_URL, echo=True)


def get_db():
    """
    Dependency to provide a database session.
    Ensures the session is properly closed after use.
    """
    with Session(engine) as session:
        yield session
