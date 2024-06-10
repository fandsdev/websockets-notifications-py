from typing import NamedTuple, NewType

UserId = NewType("UserId", str)
Event = NewType("Event", str)


class DecodedValidToken(NamedTuple):
    sub: UserId
    exp: int
