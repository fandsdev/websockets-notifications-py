import pytest

from app.conf import Settings

pytest_plugins = [
    "app.fixtures",
    "storage.fixtures",
]


@pytest.fixture(autouse=True)
def settings(mocker):
    mock = mocker.patch(
        "app.conf.get_app_settings",
        return_value=Settings(
            BROKER_URL="amqp://guest:guest@localhost/",
            BROKER_EXCHANGE="test-exchange",
            BROKER_ROUTING_KEYS=["test-routing-key", "ya-test-routing-key"],
            WEBSOCKETS_HOST="localhost",
            WEBSOCKETS_PORT=50000,
            WEBSOCKETS_PATH="/v2/test-subscription-websocket",
            AUTH_JWKS_URL="https://auth.test.com/auth/realms/test-realm/protocol/openid-connect/certs",
            AUTH_SUPPORTED_SIGNING_ALGORITHMS=["RS256"],
        ),
    )

    return mock.return_value
