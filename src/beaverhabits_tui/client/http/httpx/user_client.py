from pymonad.either import Either

from functional.alias import Error
from beaverhabits_tui.models.user import User

from .http_client import HttpClient


class UserClient:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def get_me(self) -> Either[Error, User]:
        raise NotImplementedError("Stub: not implemented yet")
