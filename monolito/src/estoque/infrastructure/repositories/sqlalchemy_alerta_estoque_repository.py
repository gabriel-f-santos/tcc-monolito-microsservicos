from uuid import UUID

from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.estoque.domain.entities.alerta_estoque import AlertaEstoque
from src.estoque.domain.repositories.alerta_estoque_repository import AlertaEstoqueRepository
from src.shared.infrastructure.database.base import Base


class AlertaEstoqueModel(Base):
    __tablename__ = "alertas_estoque"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    item_estoque_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    tipo = Column(String(50), nullable=False, default="ESTOQUE_BAIXO")
    saldo_atual = Column(Integer, nullable=False)
    estoque_minimo = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> AlertaEstoque:
        return AlertaEstoque(
            id=self.id,
            item_estoque_id=self.item_estoque_id,
            tipo=self.tipo,
            saldo_atual=self.saldo_atual,
            estoque_minimo=self.estoque_minimo,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, alerta: AlertaEstoque) -> "AlertaEstoqueModel":
        return cls(
            id=alerta.id,
            item_estoque_id=alerta.item_estoque_id,
            tipo=alerta.tipo,
            saldo_atual=alerta.saldo_atual,
            estoque_minimo=alerta.estoque_minimo,
            criado_em=alerta.criado_em,
            atualizado_em=alerta.atualizado_em,
        )


class SQLAlchemyAlertaEstoqueRepository(AlertaEstoqueRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_by_id(self, entity_id: UUID) -> AlertaEstoque | None:
        with self.session_factory() as session:
            model = session.get(AlertaEstoqueModel, entity_id)
            return model.to_domain() if model else None

    def list_by_item(self, item_estoque_id: UUID) -> list[AlertaEstoque]:
        with self.session_factory() as session:
            stmt = (
                select(AlertaEstoqueModel)
                .where(AlertaEstoqueModel.item_estoque_id == item_estoque_id)
                .order_by(AlertaEstoqueModel.criado_em.asc())
            )
            models = session.execute(stmt).scalars().all()
            return [m.to_domain() for m in models]

    def save(self, entity: AlertaEstoque) -> AlertaEstoque:
        with self.session_factory() as session:
            model = AlertaEstoqueModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def delete(self, entity_id: UUID) -> None:
        with self.session_factory() as session:
            model = session.get(AlertaEstoqueModel, entity_id)
            if model:
                session.delete(model)
                session.commit()
