from typing import NewType, NamedTuple

UserId = NewType("UserId", str)
Event = NewType("Event", str)
BrokerRoutingKey = NewType("BrokerRoutingKey", str)


class DecodedValidToken(NamedTuple):
    sub: UserId
    exp: int
