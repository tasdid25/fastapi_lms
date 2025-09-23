from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings


class Base(DeclarativeBase):
	pass


def _create_engine():
	settings = get_settings()
	connect_args = {}
	# SQLite needs check_same_thread disabled in many local cases
	if settings.DATABASE_URL.startswith("sqlite"):
		connect_args = {"check_same_thread": False}
	return create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
	"""FastAPI dependency to provide a DB session."""
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()


def init_db():
	from . import models  # ensure models are imported and mapped
	# Ensure a clean schema for tests and local runs
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
	init_db()
	print("Database initialized.")