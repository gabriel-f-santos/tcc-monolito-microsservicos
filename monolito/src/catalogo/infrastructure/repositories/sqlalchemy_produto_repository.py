from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

from src.catalogo.domain.entities.produto import Produto
from src.catalogo.domain.repositories.produto_repository import ProdutoRepository
from src.catalogo.domain.value_objects.dinheiro import Dinheiro
from src.catalogo.domain.value_objects.sku import SKU
from src.shared.infrastructure.database.base import Base


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(String(1000), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria_id = Column(PG_UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> Produto:
        return Produto(
            id=self.id,
            sku=SKU(valor=self.sku),
            nome=self.nome,
            descricao=self.descricao,
            preco=Dinheiro(valor=Decimal(str(self.preco))),
            categoria_id=self.categoria_id,
            ativo=self.ativo,
            criado_em=self.criado_em,
            atualizado_em=self.atualizado_em,
        )

    @classmethod
    def from_domain(cls, produto: Produto) -> "ProdutoModel":
        return cls(
            id=produto.id,
            sku=produto.sku.valor,
            nome=produto.nome,
            descricao=produto.descricao,
            preco=produto.preco.valor,
            categoria_id=produto.categoria_id,
            ativo=produto.ativo,
            criado_em=produto.criado_em,
            atualizado_em=produto.atualizado_em,
        )


class SQLAlchemyProdutoRepository(ProdutoRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def get_by_id(self, entity_id: UUID) -> Produto | None:
        with self.session_factory() as session:
            model = session.get(ProdutoModel, entity_id)
            return model.to_domain() if model else None

    def get_by_sku(self, sku: str) -> Produto | None:
        with self.session_factory() as session:
            stmt = select(ProdutoModel).where(ProdutoModel.sku == sku)
            model = session.execute(stmt).scalar_one_or_none()
            return model.to_domain() if model else None

    def list_filtered(
        self,
        categoria_id: UUID | None = None,
        ativo: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Produto]:
        with self.session_factory() as session:
            stmt = select(ProdutoModel)
            if categoria_id is not None:
                stmt = stmt.where(ProdutoModel.categoria_id == categoria_id)
            if ativo is not None:
                stmt = stmt.where(ProdutoModel.ativo == ativo)
            stmt = stmt.offset((page - 1) * size).limit(size)
            models = session.execute(stmt).scalars().all()
            return [m.to_domain() for m in models]

    def save(self, entity: Produto) -> Produto:
        with self.session_factory() as session:
            model = ProdutoModel.from_domain(entity)
            session.merge(model)
            session.commit()
            return entity

    def delete(self, entity_id: UUID) -> None:
        with self.session_factory() as session:
            model = session.get(ProdutoModel, entity_id)
            if model:
                session.delete(model)
                session.commit()
