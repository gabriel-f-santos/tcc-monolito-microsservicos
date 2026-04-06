from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.catalogo.application.use_cases.buscar_categoria import BuscarCategoriaUseCase
from src.catalogo.application.use_cases.criar_categoria import CriarCategoriaDTO, CriarCategoriaUseCase
from src.catalogo.application.use_cases.listar_categorias import ListarCategoriasUseCase
from src.catalogo.container import CatalogoContainer
from src.catalogo.presentation.schemas import CategoriaResponse, CriarCategoriaRequest

router = APIRouter(prefix="/api/v1/categorias", tags=["categorias"])


@router.post("", response_model=CategoriaResponse, status_code=201)
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


@router.get("", response_model=list[CategoriaResponse])
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


@router.get("/{categoria_id}", response_model=CategoriaResponse)
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
