from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.application.use_cases.login import LoginDTO, LoginUseCase
from src.auth.application.use_cases.registrar import RegistrarDTO, RegistrarUseCase
from src.auth.container import AuthContainer
from src.auth.presentation.schemas import (
    LoginRequest,
    RegistrarRequest,
    TokenResponse,
    UsuarioResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/registrar", response_model=UsuarioResponse, status_code=201)
@inject
def registrar(
    body: RegistrarRequest,
    use_case: RegistrarUseCase = Depends(Provide[AuthContainer.registrar]),
):
    usuario = use_case.execute(RegistrarDTO(nome=body.nome, email=body.email, senha=body.senha))
    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        criado_em=usuario.criado_em,
    )


@router.post("/login", response_model=TokenResponse)
@inject
def login(
    body: LoginRequest,
    use_case: LoginUseCase = Depends(Provide[AuthContainer.login]),
):
    result = use_case.execute(LoginDTO(email=body.email, senha=body.senha))
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)
