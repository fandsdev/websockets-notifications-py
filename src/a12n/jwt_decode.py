from typing import Any

import jwt

from app.conf import get_app_settings
from app.types import DecodedValidToken


def decode(jwt_token: str, **kwargs: Any) -> DecodedValidToken:
    """Validate and decode a JWT token with public key.

    Adjust validation parameters to project requirements (like algorithms, required claims, etc).
    """
    decoded = jwt.decode(jwt=jwt_token, key=get_app_settings().JWT_PUBLIC_KEY, algorithms=["RS256"], **kwargs)
    return DecodedValidToken(**decoded)
