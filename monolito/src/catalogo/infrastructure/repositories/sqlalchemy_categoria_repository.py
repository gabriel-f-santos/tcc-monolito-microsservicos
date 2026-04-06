from uuid import UUID

from sqlalchemy import Column, DateTime, String, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.shared.infrastructure.database.base import Base
from src.catalogo.domain.entities.categoria import Categoria
from src.catalogo.domain.repositories.categoria_repository import CategoriaRepository


class CategoriaModel(Base):
    __tablename__ = "categorias"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(String(1000), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> Categoria:
        return Categoria(
            id=self.id,
            nome=self.nome,
            descricao=self.descricao,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, categoria: Categoria) -> "CategoriaModel":
        return cls(
            id=categoria.id,
            nome=categoria.nome,
            descricao=categoria.descricao,
            criado_em=categoria.criado_em,
            atualizado_em=categoria.atualizado_em,
        )


class SQLAlchemyCategoriaRepository(CategoriaRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_by_id(self, entity_id: UUID) -> Categoria | None:
        with self.session_factory() as session:
            model = session.get(CategoriaModel, entity_id)
            return model.to_domain() if model else None

    def get_by_nome(self, nome: str) -> Categoria | None:
        with self.session_factory() as session:
            stmt = select(CategoriaModel).where(CategoriaModel.nome == nome)
            model = session.execute(stmt).scalar_one_or_none()
            return model.to_domain() if model else None

    def list_all(self) -> list[Categoria]:
        with self.session_factory() as session:
            stmt = select(CategoriaModel)
            models = session.execute(stmt).scalars().all()
            return [m.to_domain() for m in models]

    def save(self, entity: Categoria) -> Categoria:
        with self.session_factory() as session:
            model = CategoriaModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def delete(self, entity_id: UUID) -> None:
        with self.session_factory() as session:
            model = session.get(CategoriaModel, entity_id)
            if model:
                session.delete(model)
                session.commit()
