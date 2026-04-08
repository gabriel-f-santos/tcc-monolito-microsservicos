"""SQLAlchemy models — todas as tabelas num unico arquivo (MVC tradicional)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    senha_hash = Column(String(256), nullable=False)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(String(1000), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Produto(Base):
    __tablename__ = "produtos"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(String(1000), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria_id = Column(PG_UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ItemEstoque(Base):
    __tablename__ = "itens_estoque"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True, index=True)
    sku = Column(String(50), nullable=False)
    nome_produto = Column(String(200), nullable=False)
    categoria_nome = Column(String(100), nullable=False)
    saldo = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Movimentacao(Base):
    __tablename__ = "movimentacoes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_estoque_id = Column(PG_UUID(as_uuid=True), ForeignKey("itens_estoque.id"), nullable=False)
    tipo = Column(String(10), nullable=False)  # ENTRADA ou SAIDA
    quantidade = Column(Integer, nullable=False)
    lote = Column(String(100), nullable=True)
    motivo = Column(String(500), nullable=True)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
