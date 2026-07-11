from __future__ import annotations

import httpx
from pymonad.either import Either, Left, Right
from pymonad.maybe import Just

from beaverhabits_tui.models.habit import HabitDetail, HabitLite
from functional.alias import Error

from .http_client import HttpClient


class HabitsClient:
    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def list_habits(self, status: str = "active") -> Either[Error, list[HabitLite]]:
        result = self.http_client.get("/api/v1/habits", params={"status": status})
        return result.either(
            lambda error: Left(error),
            lambda response: self._parse_list_habits(response),
        )

    def get_habit(self, id: str) -> Either[Error, HabitDetail]:
        result = self.http_client.get(f"/api/v1/habits/{id}")
        return result.either(
            lambda error: Left(error),
            lambda response: self._parse_get_habit(response),
        )

    @staticmethod
    def _parse_list_habits(response: httpx.Response) -> Either[Error, list[HabitLite]]:
        if response.status_code == 200:
            try:
                data = response.json()
                return Right([HabitLite.model_validate(item) for item in data])
            except Exception as e:
                return Left(Error(str(e), Just(e)))
        if response.status_code == 401:
            return Left(Error("not authenticated"))
        if response.status_code == 404:
            return Left(Error("Habit not found"))
        return Left(
            Error(
                f"Unexpected status: {response.status_code}",
                Just(Exception(f"HTTP {response.status_code}")),
            )
        )

    @staticmethod
    def _parse_get_habit(response: httpx.Response) -> Either[Error, HabitDetail]:
        if response.status_code == 200:
            try:
                data = response.json()
                return Right(HabitDetail.model_validate(data))
            except Exception as e:
                return Left(Error(str(e), Just(e)))
        if response.status_code == 401:
            return Left(Error("not authenticated"))
        if response.status_code == 404:
            return Left(Error("Habit not found"))
        return Left(
            Error(
                f"Unexpected status: {response.status_code}",
                Just(Exception(f"HTTP {response.status_code}")),
            )
        )
