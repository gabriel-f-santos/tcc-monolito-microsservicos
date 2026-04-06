from uuid import UUID

from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.estoque.domain.entities.movimentacao import Movimentacao
from src.estoque.domain.repositories.movimentacao_repository import MovimentacaoRepository
from src.estoque.domain.value_objects.tipo_movimentacao import TipoMovimentacao
from src.shared.infrastructure.database.base import Base


class MovimentacaoModel(Base):
    __tablename__ = "movimentacoes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    item_estoque_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    tipo = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    lote = Column(String(100), nullable=True)
    motivo = Column(String(500), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> Movimentacao:
        return Movimentacao(
            id=self.id,
            item_estoque_id=self.item_estoque_id,
            tipo=TipoMovimentacao(self.tipo),
            quantidade=self.quantidade,
            lote=self.lote,
            motivo=self.motivo,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, mov: Movimentacao) -> "MovimentacaoModel":
        return cls(
            id=mov.id,
            item_estoque_id=mov.item_estoque_id,
            tipo=mov.tipo.value,
            quantidade=mov.quantidade,
            lote=mov.lote,
            motivo=mov.motivo,
            criado_em=mov.criado_em,
            atualizado_em=mov.atualizado_em,
        )


class SQLAlchemyMovimentacaoRepository(MovimentacaoRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def save(self, entity: Movimentacao) -> Movimentacao:
        with self.session_factory() as session:
            model = MovimentacaoModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def list_by_item(
        self,
        item_estoque_id: UUID,
        tipo: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Movimentacao]:
        with self.session_factory() as session:
            stmt = select(MovimentacaoModel).where(
                MovimentacaoModel.item_estoque_id == item_estoque_id
            )
            if tipo is not None:
                stmt = stmt.where(MovimentacaoModel.tipo == tipo)
            stmt = stmt.order_by(MovimentacaoModel.criado_em.desc())
            stmt = stmt.offset((page - 1) * size).limit(size)
            models = session.execute(stmt).scalars().all()
            return [m.to_domain() for m in models]
