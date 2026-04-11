from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt, JWTError

from src.domain.services.token_service import TokenService
from src.domain.exceptions.auth import TokenInvalido


class JoseTokenService(TokenService):
    def __init__(self, secret: str, expiration_hours: int = 24):
        self._secret = secret
        self._expiration_hours = expiration_hours

    def generate_token(self, user_id: UUID, email: str) -> str:
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=self._expiration_hours),
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._secret, algorithms=["HS256"])
            return {"user_id": payload["sub"], "email": payload["email"]}
        except JWTError:
            raise TokenInvalido()
