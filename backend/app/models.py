"""Pydantic models mirroring the openapi.yaml schemas.

`extra="forbid"` matches the spec's `additionalProperties: false`.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

GameMode = Literal["walls", "wrap"]

# A board coordinate is a non-negative integer; a Cell is exactly [x, y].
Coord = Annotated[int, Field(ge=0)]
Cell = tuple[Coord, Coord]


class Strict(BaseModel):
    """Base model that rejects unknown properties."""

    model_config = ConfigDict(extra="forbid")


class User(Strict):
    id: str
    username: str


class Credentials(Strict):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthResult(Strict):
    user: User
    token: str


class LeaderboardEntry(Strict):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    createdAt: int  # unix ms


class ActiveGame(Strict):
    id: str
    userId: str
    username: str
    mode: GameMode
    score: int = Field(ge=0)
    snake: list[Cell] = Field(min_length=1)
    food: Cell
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    alive: bool
    updatedAt: int  # unix ms


class SubmitScoreRequest(Strict):
    mode: GameMode
    score: int = Field(ge=0)


class StartGameRequest(Strict):
    mode: GameMode
    snake: list[Cell] = Field(min_length=1)
    food: Cell
    score: int = Field(ge=0)
    alive: bool
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class UpdateGameRequest(Strict):
    model_config = ConfigDict(extra="forbid")

    snake: list[Cell] | None = Field(default=None, min_length=1)
    food: Cell | None = None
    score: int | None = Field(default=None, ge=0)
    alive: bool | None = None
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)

    def changes(self) -> dict:
        """Only the fields the client actually sent (PATCH semantics)."""
        return self.model_dump(exclude_unset=True)


class Error(Strict):
    message: str
