"""Security services."""

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import jwt

from src.configurations import Config
from src.schemas import TokenData


config = Config()
http_bearer = HTTPBearer()


def encode_token(token_data: TokenData) -> str:
    """Create token."""
    payload = token_data.dict()
    payload["exp"] = datetime.utcnow() + timedelta(days=4)
    return jwt.encode(payload, config.JWT_SECRET)


def decode_token(token: HTTPAuthorizationCredentials = Depends(http_bearer)) -> TokenData:
    """Get data from token."""
    try:
        decoded = jwt.decode(token.credentials, config.JWT_SECRET, algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    return TokenData.parse_obj(decoded)
