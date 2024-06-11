import pytest
from datetime import UTC, datetime

import jwt

from a12n import jwt_decode
from app.types import DecodedValidToken


def test_decode_valid_token(jwt_user_valid_token):
    decoded = jwt_decode.decode(jwt_user_valid_token)

    assert isinstance(decoded, DecodedValidToken)
    assert decoded.sub == "user"
    assert decoded.exp == 4700000000


@pytest.mark.freeze_time(datetime.fromtimestamp(4700000001, tz=UTC))
def test_decode_expired_token(jwt_user_valid_token):
    with pytest.raises(jwt.ExpiredSignatureError, match="Signature has expired"):
        jwt_decode.decode(jwt_user_valid_token)
