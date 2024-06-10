import pytest
from contextlib import nullcontext as does_not_raise

from a12n.jwk_client import AsyncJWKClientException

pytestmark = [
    pytest.mark.usefixtures("mock_success_response"),
]


async def test_decode_token_and_return_valid_data(jwk_client, token):
    with does_not_raise():
        decoded_valid_token = await jwk_client.decode(token)

    assert decoded_valid_token.sub == "auth0|653c3260a30448c594a69e12"
    assert decoded_valid_token.exp == 4852128170  # 2123-10-05 00:22:50 GMT+03:00


async def test_raise_if_token_is_not_valid(jwk_client, expired_token):
    with pytest.raises(AsyncJWKClientException, match="Signature has expired"):
        await jwk_client.decode(expired_token)


async def test_decode_token_without_validation_if_signature_verification_disable(jwk_client, expired_token):
    with does_not_raise():
        expired_token = await jwk_client.decode(expired_token, options={"verify_signature": False, "verify_exp": False})

    assert expired_token.sub == "auth0|653c3260a30448c594a69e12"


async def test_raise_if_token_signed_with_not_supported_algorithm(jwk_client, token):
    jwk_client.supported_signing_algorithms = ["EdDSA"]

    with pytest.raises(AsyncJWKClientException, match="The specified alg value is not allowed"):
        await jwk_client.decode(token)
