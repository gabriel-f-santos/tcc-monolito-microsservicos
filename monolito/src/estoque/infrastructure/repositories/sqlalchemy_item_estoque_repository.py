from uuid import UUID

from sqlalchemy import Column, DateTime, Integer, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.shared.infrastructure.database.base import Base


class ItemEstoqueModel(Base):
    __tablename__ = "itens_estoque"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    produto_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True, index=True)
    saldo = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> ItemEstoque:
        return ItemEstoque(
            id=self.id,
            produto_id=self.produto_id,
            saldo=self.saldo,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, item: ItemEstoque) -> "ItemEstoqueModel":
        return cls(
            id=item.id,
            produto_id=item.produto_id,
            saldo=item.saldo,
            criado_em=item.criado_em,
            atualizado_em=item.atualizado_em,
        )


class SQLAlchemyItemEstoqueRepository(ItemEstoqueRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_by_id(self, entity_id: UUID) -> ItemEstoque | None:
        with self.session_factory() as session:
            model = session.get(ItemEstoqueModel, entity_id)
            return model.to_domain() if model else None

    def get_by_produto_id(self, produto_id: UUID) -> ItemEstoque | None:
        with self.session_factory() as session:
            stmt = select(ItemEstoqueModel).where(ItemEstoqueModel.produto_id == produto_id)
            model = session.execute(stmt).scalar_one_or_none()
            return model.to_domain() if model else None

    def save(self, entity: ItemEstoque) -> ItemEstoque:
        with self.session_factory() as session:
            model = ItemEstoqueModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def delete(self, entity_id: UUID) -> None:
        with self.session_factory() as session:
            model = session.get(ItemEstoqueModel, entity_id)
            if model:
                session.delete(model)
                session.commit()
