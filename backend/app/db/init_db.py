import logging
from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.base import Base
from app.models import User, Video, Clip, Project, Compilation

logger = logging.getLogger(__name__)


def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def reset_db() -> None:
    # Drop all tables and recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
