import httpx
from httpx import ConnectError, TimeoutException
from pymonad.either import Either, Left, Right
from pymonad.maybe import Just

from functional.alias import Error


class HttpClient:
    """Minimal httpx-based HTTP client returning Either[Error, httpx.Response].

    Every request is wrapped in Either — never raises.
    """

    def __init__(self, base_url: str, extra_headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.extra_headers = extra_headers or {}

    def get(self, path: str, params: dict | None = None) -> Either[Error, httpx.Response]:
        url = self._build_url(path)
        try:
            response = httpx.get(url, headers=self.extra_headers, params=params, timeout=30)
            return Right(response)
        except ConnectError:
            return Left(Error("Connection refused"))
        except TimeoutException:
            return Left(Error("Request timed out"))
        except Exception as e:
            return Left(Error(str(e), Just(e)))

    def _build_url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"
