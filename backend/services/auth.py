from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, cast

import jwt
import redis

from schemas import UserSchema
from dependencies import redis_con
from settings import Secret
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


# get secrete key
settings = Secret()

ALGORITHM = "HS256"
TOKEN_EXPIRE_MIN = 4320 # 3 days


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        secret: str = settings.SECRET_KEY,
        algorithm: str = ALGORITHM,
        redisCon: redis.Redis = Depends(redis_con),
        auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)
        self.secret = secret
        self.algorithm = algorithm
        self.redis = redisCon

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token.",
                )
            if is_token_revoked(credentials.credentials, self.redis):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token is revoked",
                )

            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        payload = decode_jwt(jwtoken, self.secret, self.algorithm)
        return payload is not None


def decode_jwt(jwtoken: str, secret: str, algorithm: Optional[str] = "HS256") -> dict[Any, Any]:
    try:
        payload = jwt.decode(jwtoken, secret, algorithms=[algorithm])
        return cast(dict[Any, Any], payload)
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.InvalidTokenError:
        return {}


def get_current_user(token: str = Depends(JWTBearer())) -> UserSchema:
    try:
        if payload := decode_jwt(token, settings.SECRET_KEY):
            return UserSchema(
                email=payload["email"],
                phone_number=payload["phone_number"],
                full_name=payload["full_name"]
            )
        raise ValueError("payload is empty")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def sign_jwt(
    payload: dict,
    secret: str,
    expires_min: Optional[timedelta] = None,
) -> str:
    payload["exp"] = datetime.now(timezone.utc) +
        timedelta(
            min=expires_min if expires_min else TOKEN_EXPIRE_MIN)
    token = jwt.encode(payload, secret, algorithm=ALGORITHM)
    return token


def is_token_revoked(token: str, redis: redis.Redis) -> bool:
    """
    Check if token has been revoked
    """
    return redis.sismember("revoked_tokens", token)


def revoke_token(token: str, redis: redis.Redis) -> None:
    """
    Add token to revoked tokens collection
    """
    redis.sadd("revoked_tokens", token)


def generate_access_token(
    user: UserSchema,
    expires_minutes: Union[int, None] = None,
) -> str:
    payload = {
        "email":user.email,
        # "phone_number": user.phone_number,
        "full_name": user.full_name
    }
    secret: str = settings.SECRET_KEY
    token = sign_jwt(payload, secret=secret, expires_min=expires_minutes
    return token
