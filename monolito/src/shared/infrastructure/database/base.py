from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base compartilhada para todos os models SQLAlchemy.
    Todos os BCs herdam desta classe para que Alembic e create_all
    descubram todas as tabelas a partir de um unico metadata."""
    pass
