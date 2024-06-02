import pytest

import httpx
import jwt
from jwt.api_jwk import PyJWK
from respx import Route

from a12n.jwk_client import AsyncJWKClientException


@pytest.fixture
def mock_jwk_endpoint_first_call_wrong_kid_second_call_correct_kid(mock_jwk_endpoint: Route, matching_kid_data, not_matching_kid_data):
    return mock_jwk_endpoint.mock(
        side_effect=[
            httpx.Response(status_code=200, json=not_matching_kid_data),
            httpx.Response(status_code=200, json=matching_kid_data),
        ]
    )


async def test_get_signing_key_from_jwt(jwk_client, token, mock_success_response):
    signing_key = await jwk_client.get_signing_key_from_jwt(token)

    assert isinstance(signing_key, PyJWK)
    assert signing_key.key_id == "3Lr8nN8uGopPILfQoPj_D"


async def test_token_could_be_decoded_with_signing_key(jwk_client, token, mock_success_response):
    signing_key = await jwk_client.get_signing_key_from_jwt(token)

    data = jwt.decode(
        jwt=token,
        key=signing_key.key,
        algorithms=["RS256"],
        options={"verify_aud": False},
    )

    assert data == {
        "iss": "https://dev-prntdmo163scls4x.us.auth0.com/",
        "aud": "1WSbGXFRyaKClLroXvmy9WvwkeKGoRok",
        "iat": 1698528170,
        "exp": 4852128170,
        "sub": "auth0|653c3260a30448c594a69e12",
        "sid": "90FwXSCHU-wCwBf4cV2CsYNzA2Wbx3Tq",
        "nonce": "15a5b63f73290702e70ebfbe079881bb",
    }


async def test_raise_if_jwt_key_not_match_fetched_jwk_set(jwk_client, mock_jwk_endpoint, not_matching_kid_data, token):
    mock_jwk_endpoint.respond(json=not_matching_kid_data)

    with pytest.raises(AsyncJWKClientException, match="Unable to find a signing key"):
        await jwk_client.get_signing_key_from_jwt(token)


@pytest.mark.usefixtures("mock_jwk_endpoint_first_call_wrong_kid_second_call_correct_kid")
async def test_refresh_jwk_set_if_cached_jwk_set_not_match_jwt_kid(jwk_client, respx_mock, token):
    signing_key = await jwk_client.get_signing_key_from_jwt(token)

    assert signing_key.key_id == "3Lr8nN8uGopPILfQoPj_D"
    assert respx_mock.calls.call_count == 2
