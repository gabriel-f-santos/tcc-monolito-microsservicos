from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.estoque.application.use_cases.buscar_item import BuscarItemUseCase
from src.estoque.application.use_cases.listar_itens import ListarItensUseCase
from src.estoque.application.use_cases.listar_movimentacoes import ListarMovimentacoesUseCase
from src.estoque.application.use_cases.registrar_entrada import (
    RegistrarEntradaDTO,
    RegistrarEntradaUseCase,
)
from src.estoque.application.use_cases.registrar_saida import (
    RegistrarSaidaDTO,
    RegistrarSaidaUseCase,
)
from src.estoque.container import EstoqueContainer
from src.estoque.presentation.schemas import (
    ItemEstoqueResponse,
    MovimentacaoResponse,
    RegistrarEntradaRequest,
    RegistrarSaidaRequest,
)

router = APIRouter(tags=["estoque"])


def _build_item_response(item) -> ItemEstoqueResponse:
    return ItemEstoqueResponse(
        id=item.id,
        produto_id=item.produto_id,
        sku=item.sku,
        nome_produto=item.nome_produto,
        categoria_nome=item.categoria_nome,
        saldo=item.saldo,
        ativo=item.ativo,
        criado_em=item.criado_em,
    )


def _build_mov_response(mov) -> MovimentacaoResponse:
    return MovimentacaoResponse(
        id=mov.id,
        item_estoque_id=mov.item_estoque_id,
        tipo=mov.tipo.value,
        quantidade=mov.quantidade,
        lote=mov.lote,
        motivo=mov.motivo,
        criado_em=mov.criado_em,
    )


@router.post("/api/v1/estoque/{item_id}/entrada", response_model=MovimentacaoResponse, status_code=201)
@inject
def registrar_entrada(
    item_id: UUID,
    body: RegistrarEntradaRequest,
    use_case: RegistrarEntradaUseCase = Depends(Provide[EstoqueContainer.registrar_entrada]),
):
    mov = use_case.execute(
        RegistrarEntradaDTO(
            item_estoque_id=item_id,
            quantidade=body.quantidade,
            lote=body.lote,
            motivo=body.motivo,
        )
    )
    return _build_mov_response(mov)


@router.post("/api/v1/estoque/{item_id}/saida", response_model=MovimentacaoResponse, status_code=201)
@inject
def registrar_saida(
    item_id: UUID,
    body: RegistrarSaidaRequest,
    use_case: RegistrarSaidaUseCase = Depends(Provide[EstoqueContainer.registrar_saida]),
):
    mov = use_case.execute(
        RegistrarSaidaDTO(
            item_estoque_id=item_id,
            quantidade=body.quantidade,
            motivo=body.motivo,
        )
    )
    return _build_mov_response(mov)


@router.get("/api/v1/estoque", response_model=list[ItemEstoqueResponse])
@inject
def listar_itens(
    saldo_min: int | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    use_case: ListarItensUseCase = Depends(Provide[EstoqueContainer.listar_itens]),
):
    itens = use_case.execute(saldo_min=saldo_min, page=page, size=size)
    return [_build_item_response(i) for i in itens]


@router.get("/api/v1/estoque/produto/{produto_id}", response_model=ItemEstoqueResponse)
@inject
def buscar_item_por_produto(
    produto_id: UUID,
    use_case: BuscarItemUseCase = Depends(Provide[EstoqueContainer.buscar_item]),
):
    item = use_case.execute_por_produto(produto_id)
    return _build_item_response(item)


@router.get("/api/v1/estoque/{item_id}", response_model=ItemEstoqueResponse)
@inject
def buscar_item(
    item_id: UUID,
    use_case: BuscarItemUseCase = Depends(Provide[EstoqueContainer.buscar_item]),
):
    item = use_case.execute(item_id)
    return _build_item_response(item)


@router.get("/api/v1/estoque/{item_id}/movimentacoes", response_model=list[MovimentacaoResponse])
@inject
def listar_movimentacoes(
    item_id: UUID,
    tipo: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    use_case: ListarMovimentacoesUseCase = Depends(Provide[EstoqueContainer.listar_movimentacoes]),
):
    movs = use_case.execute(item_estoque_id=item_id, tipo=tipo, page=page, size=size)
    return [_build_mov_response(m) for m in movs]
