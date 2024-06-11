import pytest

import jwt

from app.types import UserId


@pytest.fixture
def jwt_private_key():
    """For test purposes only. The running application should not access the private key."""
    return """-----BEGIN PRIVATE KEY-----
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
8qn2Iv/fqfJHIYs6DvxWgLy8ZoWL
-----END PRIVATE KEY-----
"""


@pytest.fixture
def jwt_public_key():
    return """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAqdnObC47NUAqOOCvOzOg
4i0KxZaTe2m7rfQe9a+rWbtkJ2TNuakN7eRshvv2UVGP4uSKEKe356v4GwP/yGAi
92XEGr0Y6ieypnhu1wi0wuK4Z62abRkvsEZdDwKQpcde1rvyuvt0YeDMh9dCi/3P
BLhcOlgvAu+6M79iWlRTZxzFe3KVzQabU8CIfgG7MXokutHUxT2dsRNfX4VwxMsW
o9o0o1QqSPJ6OOx2DwLEKat5n1w5ysIYYvkgHs36B3nPnZYc2b66uEp9AP9JlRjc
pWuH8vn3/OsvxHMErhyn+h9/H+aXRRIk/JuokqpVbPlOY8l+5z+JG6zn9onWpjcM
jQ19NP8C/CTwvcB8O+s3qEHKECkggyywCOe7EQqrB0uMU7IQ1srH8ENspuY16UQV
qQPBlYVQOywVW6+25z+ILNyPjEdzukn6Oyh9ChU+m08Tw9SsBAV2vnrkUCT1wJhC
c2X/i2WqBM4lExJu18tau0X26iKdbRZwx50OKUVn9w8AbW/iglCExYkpDs3VKH80
allIBcfAOXJ00X6jhWETT2T9U1c1KiTqNHMgBflvG17CbkKkyaFIILdYIfMkW2EA
ngpOxaBC1cLJTvXGuTx4R54wpQNyt8k/7P/r8UY+FxBlA/3Upb9LidmItvd7yvVr
zUMftEW5MYWWWnm6ZUS3Q6sCAwEAAQ==
-----END PUBLIC KEY-----
"""


@pytest.fixture
def set_jwt_public_key(settings, jwt_public_key):
    settings.JWT_PUBLIC_KEY = jwt_public_key
    return settings


@pytest.fixture
def create_jwt_for_user(jwt_private_key):
    def create_jwt(user_id: UserId, timestamp_expired_at: int) -> str:
        payload = {
            "sub": user_id,
            "exp": timestamp_expired_at,
        }

        return jwt.encode(payload=payload, key=jwt_private_key, algorithm="RS256")

    return create_jwt


@pytest.fixture
def jwt_user_valid_token(create_jwt_for_user):
    return create_jwt_for_user(
        user_id="user",
        timestamp_expired_at=4700000000,  # year of expiration 2118
    )
