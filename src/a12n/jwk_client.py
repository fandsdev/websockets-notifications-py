import asyncio
from dataclasses import dataclass
import json
import logging

import httpx
import jwt
from jwt.api_jwk import PyJWK
from jwt.api_jwk import PyJWKSet
from jwt.api_jwt import decode_complete as decode_token
from jwt.exceptions import PyJWKSetError
from jwt.jwk_set_cache import JWKSetCache


from app.types import DecodedValidToken


logger = logging.getLogger(__name__)


class AsyncJWKClientException(Exception):
    pass


@dataclass
class AsyncJWKClient:
    """
    Inspired and partially copy-pasted from 'jwt.jwks_client.PyJWKClient'.
    The purpose is the same but querying the JWKS endpoint is async.
    """

    jwks_url: str
    supported_signing_algorithms: list[str]
    cache_lifespan: int = 1 * 60 * 60 * 24  # 1 day

    def __post_init__(self) -> None:
        self.jwk_set_cache = JWKSetCache(self.cache_lifespan)

        # Lock is used to synchronize coroutines to prevent multiple concurrent attempts to refresh cached jwk_set
        self.fetch_data_lock = asyncio.Lock()

    async def fetch_data(self) -> PyJWKSet:
        try:
            async with self.fetch_data_lock:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url=self.jwks_url)

                response.raise_for_status()
                jwk_set_data = response.json()

                if not isinstance(jwk_set_data, dict):
                    raise AsyncJWKClientException("Fetched data from JWKS endpoint is JSON but not an object")

                jwk_set = PyJWKSet.from_dict(jwk_set_data)
                self.jwk_set_cache.put(jwk_set)

                logger.info(
                    "Signing keys fetched. Key ids: '%s'",
                    (" ,").join([key.key_id for key in jwk_set.keys if key.key_id]),
                )

                return jwk_set

        except httpx.HTTPError as exc:
            raise AsyncJWKClientException(f"Fail to fetch data from JWKS endpoint: '{exc}'") from exc
        except json.JSONDecodeError as exc:
            raise AsyncJWKClientException(f"Fetched data from JWKS endpoint not a JSON: '{exc}'") from exc
        except PyJWKSetError as exc:
            raise AsyncJWKClientException(exc) from exc

    async def get_jwk_set(self, refresh: bool = False) -> PyJWKSet:
        jwk_set: PyJWKSet | None = None

        while self.fetch_data_lock.locked():
            await asyncio.sleep(0)

        if not refresh:
            jwk_set = self.jwk_set_cache.get()

        if jwk_set is None:
            jwk_set = await self.fetch_data()

        return jwk_set

    async def get_signing_keys(self, refresh: bool = False) -> list[PyJWK]:
        jwk_set = await self.get_jwk_set(refresh)

        signing_keys = [
            jwk_set_key
            for jwk_set_key in jwk_set.keys
            if jwk_set_key.public_key_use
            in [
                "sig",
                None,
            ]
            and jwk_set_key.key_id
        ]

        if not signing_keys:
            raise AsyncJWKClientException("The JWKS endpoint did not contain any signing keys")

        return signing_keys

    async def get_signing_key(self, kid: str) -> PyJWK:
        signing_keys = await self.get_signing_keys()
        signing_key = self.match_kid(signing_keys, kid)

        if not signing_key:
            # If no matching signing key from the jwk set, refresh the jwk set and try again.
            signing_keys = await self.get_signing_keys(refresh=True)
            signing_key = self.match_kid(signing_keys, kid)

            if not signing_key:
                raise AsyncJWKClientException(f"Unable to find a signing key that matches: '{kid}'")

        return signing_key

    async def get_signing_key_from_jwt(self, token: str) -> PyJWK:
        unverified = decode_token(token, options={"verify_signature": False})
        header = unverified["header"]
        return await self.get_signing_key(header.get("kid"))

    @staticmethod
    def match_kid(signing_keys: list[PyJWK], kid: str) -> PyJWK | None:
        signing_key = None

        for key in signing_keys:
            if key.key_id == kid:
                signing_key = key
                break

        return signing_key

    async def decode(self, token: str, options: dict | None = None) -> DecodedValidToken:
        decode_options = {
            "verify_aud": False,
            "verify_exp": True,
            "verify_iat": True,
            "require": ["exp", "iat", "sub"],
        }

        if options is not None:
            decode_options.update(options)

        verify_signature = decode_options.get("verify_signature", True)

        try:
            signing_key = (await self.get_signing_key_from_jwt(token)).key if verify_signature else ""

            verified_payload = jwt.decode(
                jwt=token,
                algorithms=self.supported_signing_algorithms,
                key=signing_key,
                options=decode_options,
            )
        except jwt.PyJWTError as exc:
            raise AsyncJWKClientException(exc) from exc

        return DecodedValidToken(sub=verified_payload["sub"], exp=verified_payload["exp"])
