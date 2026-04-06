from uuid import UUID

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, registry, sessionmaker

from src.auth.domain.entities.usuario import Usuario
from src.auth.domain.repositories.usuario_repository import UsuarioRepository

mapper_registry = registry()
Base = mapper_registry.generate_base()


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    senha_hash = Column(String(256), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> Usuario:
        return Usuario(
            id=self.id,
            nome=self.nome,
            email=self.email,
            senha_hash=self.senha_hash,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, usuario: Usuario) -> "UsuarioModel":
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            senha_hash=usuario.senha_hash,
            criado_em=usuario.criado_em,
            atualizado_em=usuario.atualizado_em,
        )


class SQLAlchemyUsuarioRepository(UsuarioRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_by_id(self, entity_id: UUID) -> Usuario | None:
        with self.session_factory() as session:
            model = session.get(UsuarioModel, entity_id)
            return model.to_domain() if model else None

    def get_by_email(self, email: str) -> Usuario | None:
        with self.session_factory() as session:
            model = session.query(UsuarioModel).filter(UsuarioModel.email == email).first()
            return model.to_domain() if model else None

    def save(self, entity: Usuario) -> Usuario:
        with self.session_factory() as session:
            model = UsuarioModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def delete(self, entity_id: UUID) -> None:
        with self.session_factory() as session:
            model = session.get(UsuarioModel, entity_id)
            if model:
                session.delete(model)
                session.commit()
