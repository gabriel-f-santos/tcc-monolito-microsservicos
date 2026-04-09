"""Auth routes — registrar + login (bcrypt + JWT direto)."""
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import Usuario
from schemas import LoginRequest, RegistrarRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SECRET_KEY = "super-secret-key-monolito-mvc"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/registrar", status_code=201, response_model=UsuarioResponse)
def registrar(body: RegistrarRequest, session: Session = Depends(get_session)):
    existente = session.execute(
        select(Usuario).where(Usuario.email == body.email.lower())
    ).scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=409, detail="Email ja cadastrado")

    usuario = Usuario(
        nome=body.nome,
        email=body.email.lower(),
        senha_hash=_hash_password(body.senha),
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return UsuarioResponse.model_validate(usuario)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    usuario = session.execute(
        select(Usuario).where(Usuario.email == body.email.lower())
    ).scalar_one_or_none()
    if not usuario or not _verify_password(body.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais invalidas")

    token = _create_token(str(usuario.id))
    return TokenResponse(access_token=token)
