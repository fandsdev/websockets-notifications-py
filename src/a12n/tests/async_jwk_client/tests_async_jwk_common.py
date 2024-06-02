from jwt.jwk_set_cache import JWKSetCache


def test_create_jwk_client_with_empty_pyjwkset_cache(jwk_client):
    jwk_cache = jwk_client.jwk_set_cache

    assert isinstance(jwk_cache, JWKSetCache)
    assert jwk_cache.lifespan == 1 * 60 * 60 * 24  # one day by default
    assert jwk_cache.get() is None, "JWK set cache should be empty on init"
