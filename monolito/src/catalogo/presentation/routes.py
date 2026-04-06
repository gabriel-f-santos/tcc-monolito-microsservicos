from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.catalogo.application.use_cases.atualizar_produto import (
    AtualizarProdutoDTO,
    AtualizarProdutoUseCase,
)
from src.catalogo.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.catalogo.application.use_cases.buscar_produto import BuscarProdutoUseCase
from src.catalogo.application.use_cases.criar_categoria import CriarCategoriaDTO, CriarCategoriaUseCase
from src.catalogo.application.use_cases.criar_produto import CriarProdutoDTO, CriarProdutoUseCase
from src.catalogo.application.use_cases.desativar_produto import DesativarProdutoUseCase
from src.catalogo.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.catalogo.application.use_cases.listar_produtos import ListarProdutosUseCase
from src.catalogo.container import CatalogoContainer
from src.catalogo.presentation.schemas import (
    AtualizarProdutoRequest,
    CategoriaResponse,
    CategoriaNested,
    CriarCategoriaRequest,
    CriarProdutoRequest,
    ProdutoResponse,
)

router = APIRouter(tags=["categorias"])

# --- Categoria routes ---


@router.post("/api/v1/categorias", response_model=CategoriaResponse, status_code=201)
@inject
def criar_categoria(
    body: CriarCategoriaRequest,
    use_case: CriarCategoriaUseCase = Depends(Provide[CatalogoContainer.criar_categoria]),
):
    categoria = use_case.execute(CriarCategoriaDTO(nome=body.nome, descricao=body.descricao))
    return CategoriaResponse(
        id=categoria.id,
        nome=categoria.nome,
        descricao=categoria.descricao,
        criado_em=categoria.criado_em,
    )


@router.get("/api/v1/categorias", response_model=list[CategoriaResponse])
@inject
def listar_categorias(
    use_case: ListarCategoriasUseCase = Depends(Provide[CatalogoContainer.listar_categorias]),
):
    categorias = use_case.execute()
    return [
        CategoriaResponse(
            id=c.id,
            nome=c.nome,
            descricao=c.descricao,
            criado_em=c.criado_em,
        )
        for c in categorias
    ]


@router.get("/api/v1/categorias/{categoria_id}", response_model=CategoriaResponse)
@inject
def buscar_categoria(
    categoria_id: UUID,
    use_case: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    categoria = use_case.execute(categoria_id)
    return CategoriaResponse(
        id=categoria.id,
        nome=categoria.nome,
        descricao=categoria.descricao,
        criado_em=categoria.criado_em,
    )


# --- Produto routes ---


def _build_produto_response(produto, categoria) -> ProdutoResponse:
    return ProdutoResponse(
        id=produto.id,
        sku=produto.sku.valor,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco.valor,
        categoria=CategoriaNested(id=categoria.id, nome=categoria.nome),
        ativo=produto.ativo,
        criado_em=produto.criado_em,
        atualizado_em=produto.atualizado_em,
    )


@router.post("/api/v1/produtos", response_model=ProdutoResponse, status_code=201)
@inject
def criar_produto(
    body: CriarProdutoRequest,
    use_case: CriarProdutoUseCase = Depends(Provide[CatalogoContainer.criar_produto]),
    buscar_cat: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    produto = use_case.execute(
        CriarProdutoDTO(
            sku=body.sku,
            nome=body.nome,
            descricao=body.descricao,
            preco=body.preco,
            categoria_id=body.categoria_id,
        )
    )
    categoria = buscar_cat.execute(produto.categoria_id)
    return _build_produto_response(produto, categoria)


@router.get("/api/v1/produtos", response_model=list[ProdutoResponse])
@inject
def listar_produtos(
    categoria_id: UUID | None = Query(None),
    ativo: bool | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    use_case: ListarProdutosUseCase = Depends(Provide[CatalogoContainer.listar_produtos]),
    buscar_cat: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    produtos = use_case.execute(categoria_id=categoria_id, ativo=ativo, page=page, size=size)
    result = []
    cat_cache: dict = {}
    for p in produtos:
        if p.categoria_id not in cat_cache:
            cat_cache[p.categoria_id] = buscar_cat.execute(p.categoria_id)
        result.append(_build_produto_response(p, cat_cache[p.categoria_id]))
    return result


@router.get("/api/v1/produtos/{produto_id}", response_model=ProdutoResponse)
@inject
def buscar_produto(
    produto_id: UUID,
    use_case: BuscarProdutoUseCase = Depends(Provide[CatalogoContainer.buscar_produto]),
    buscar_cat: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    produto = use_case.execute(produto_id)
    categoria = buscar_cat.execute(produto.categoria_id)
    return _build_produto_response(produto, categoria)


@router.put("/api/v1/produtos/{produto_id}", response_model=ProdutoResponse)
@inject
def atualizar_produto(
    produto_id: UUID,
    body: AtualizarProdutoRequest,
    use_case: AtualizarProdutoUseCase = Depends(Provide[CatalogoContainer.atualizar_produto]),
    buscar_cat: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    produto = use_case.execute(
        produto_id,
        AtualizarProdutoDTO(nome=body.nome, descricao=body.descricao, preco=body.preco),
    )
    categoria = buscar_cat.execute(produto.categoria_id)
    return _build_produto_response(produto, categoria)


@router.patch("/api/v1/produtos/{produto_id}/desativar", response_model=ProdutoResponse)
@inject
def desativar_produto(
    produto_id: UUID,
    use_case: DesativarProdutoUseCase = Depends(Provide[CatalogoContainer.desativar_produto]),
    buscar_cat: BuscarCategoriaUseCase = Depends(Provide[CatalogoContainer.buscar_categoria]),
):
    produto = use_case.execute(produto_id)
    categoria = buscar_cat.execute(produto.categoria_id)
    return _build_produto_response(produto, categoria)
