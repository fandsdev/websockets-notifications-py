import logging
import pytest

from a12n.jwk_client import AsyncJWKClientException


async def test_fetch_data_send_request(jwk_client, respx_mock, mock_success_response):
    await jwk_client.fetch_data()

    sent_request = respx_mock.calls.last.request
    assert sent_request.url == "https://auth.test.com/auth/realms/test-realm/protocol/openid-connect/certs"


async def test_fetch_data_return_fetched_data_and_cache(jwk_client, mock_success_response):
    jwk_set = await jwk_client.fetch_data()

    assert jwk_client.jwk_set_cache.get() == jwk_set
    assert len(jwk_set.keys) == 1
    assert jwk_set.keys[0].key_id == "3Lr8nN8uGopPILfQoPj_D"
    assert jwk_set.keys[0].public_key_use == "sig"
    assert jwk_set.keys[0].key_type == "RSA"


async def test_log_fetched_keys_ids(jwk_client, mock_success_response, caplog):
    caplog.set_level(logging.INFO)

    await jwk_client.fetch_data()

    assert "3Lr8nN8uGopPILfQoPj_D" in caplog.text


async def test_fetch_data_raise_on_http_error(jwk_client, mock_jwk_endpoint):
    mock_jwk_endpoint.respond(status_code=404)

    with pytest.raises(AsyncJWKClientException, match="Fail to fetch data"):
        await jwk_client.fetch_data()


async def test_fetch_data_raise_on_not_json_response(jwk_client, mock_jwk_endpoint):
    mock_jwk_endpoint.respond(content=b"not-json-content")

    with pytest.raises(AsyncJWKClientException, match="not a JSON"):
        await jwk_client.fetch_data()


async def test_fetch_data_raise_if_serialized_json_response_not_a_dict(jwk_client, mock_jwk_endpoint):
    mock_jwk_endpoint.respond(json=[])

    with pytest.raises(AsyncJWKClientException, match="is JSON but not an object"):
        await jwk_client.fetch_data()


async def test_fetch_data_raise_if_serialized_json_not_jwkset(jwk_client, mock_jwk_endpoint):
    mock_jwk_endpoint.respond(json={"keys": []})  # no keys

    with pytest.raises(AsyncJWKClientException, match="did not contain any keys"):
        await jwk_client.fetch_data()
