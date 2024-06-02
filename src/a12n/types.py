from typing import NamedTuple


class DecodedValidToken(NamedTuple):
    sub: str
    exp: int
