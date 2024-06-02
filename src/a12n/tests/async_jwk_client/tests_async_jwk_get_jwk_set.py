import asyncio
import pytest

import httpx


@pytest.fixture
async def amock_latency_success_response(mock_jwk_endpoint, matching_kid_data):
    async def latency_response(request):
        await asyncio.sleep(0.1)
        return httpx.Response(status_code=200, json=matching_kid_data)

    return mock_jwk_endpoint.mock(side_effect=latency_response)


async def test_get_jwk_set_return_jwk_key_set(jwk_client, respx_mock, mock_success_response):
    jwk_set = await jwk_client.get_jwk_set()

    assert len(jwk_set.keys) == 1
    assert respx_mock.calls.call_count == 1


async def test_get_jwk_set_is_cached(jwk_client, respx_mock, mock_success_response):
    await jwk_client.get_jwk_set()

    await jwk_client.get_jwk_set()

    assert respx_mock.calls.call_count == 1


@pytest.mark.freeze_time("2023-01-01 00:00:00")
async def test_get_jwk_set_cache_invalidated_when_lifespan_expired(jwk_client, respx_mock, freezer, mock_success_response):
    await jwk_client.get_jwk_set()
    freezer.move_to("2023-01-02 00:00:01")  # 1 day + 1 second passed

    await jwk_client.get_jwk_set()

    assert respx_mock.calls.call_count == 2


@pytest.mark.usefixtures("amock_latency_success_response")
async def test_get_jwk_set_corotines_do_not_try_to_update_cache_simultaneously(jwk_client, respx_mock):
    first_get_jwk_task = asyncio.create_task(jwk_client.get_jwk_set())
    second_get_jwk_task = asyncio.create_task(jwk_client.get_jwk_set())

    await asyncio.gather(first_get_jwk_task, second_get_jwk_task)

    assert respx_mock.calls.call_count == 1


async def test_get_jwk_set_could_be_forced_to_update_cache(jwk_client, respx_mock, mock_success_response):
    await jwk_client.get_jwk_set()

    await jwk_client.get_jwk_set(refresh=True)

    assert respx_mock.calls.call_count == 2
