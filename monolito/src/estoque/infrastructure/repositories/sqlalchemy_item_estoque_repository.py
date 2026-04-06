from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, Integer, String, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.estoque.domain.entities.item_estoque import ItemEstoque
from src.estoque.domain.repositories.item_estoque_repository import ItemEstoqueRepository
from src.shared.infrastructure.database.base import Base


class ItemEstoqueModel(Base):
    __tablename__ = "itens_estoque"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    produto_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True, index=True)
    sku = Column(String(50), nullable=False)
    nome_produto = Column(String(200), nullable=False)
    categoria_nome = Column(String(100), nullable=False)
    saldo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> ItemEstoque:
        return ItemEstoque(
            id=self.id,
            produto_id=self.produto_id,
            sku=self.sku,
            nome_produto=self.nome_produto,
            categoria_nome=self.categoria_nome,
            saldo=self.saldo,
            ativo=self.ativo,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, item: ItemEstoque) -> "ItemEstoqueModel":
        return cls(
            id=item.id,
            produto_id=item.produto_id,
            sku=item.sku,
            nome_produto=item.nome_produto,
            categoria_nome=item.categoria_nome,
            saldo=item.saldo,
            ativo=item.ativo,
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

    def list_filtered(
        self,
        saldo_min: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[ItemEstoque]:
        with self.session_factory() as session:
            stmt = select(ItemEstoqueModel)
            if saldo_min is not None:
                stmt = stmt.where(ItemEstoqueModel.saldo >= saldo_min)
            stmt = stmt.order_by(ItemEstoqueModel.criado_em.desc())
            stmt = stmt.offset((page - 1) * size).limit(size)
            models = session.execute(stmt).scalars().all()
            return [m.to_domain() for m in models]

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
