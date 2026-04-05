from uuid import UUID

from src.shared.domain.entities.base import BaseEntity


def test_base_entity_generates_uuid():
    entity = BaseEntity()
    assert isinstance(entity.id, UUID)


def test_base_entity_generates_timestamps():
    entity = BaseEntity()
    assert entity.criado_em is not None
    assert entity.atualizado_em is not None


def test_base_entity_unique_ids():
    e1 = BaseEntity()
    e2 = BaseEntity()
    assert e1.id != e2.id
