"""Offline identity contracts; unrelated to project business authorization."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocalUser:
    user_id: str
    username: str
    display_name: str


@dataclass(frozen=True)
class Credential:
    user: LocalUser
    salt: bytes
    password_hash: bytes


class IdentityStore(Protocol):
    def credential(self, username: str) -> Credential | None: ...
    def create_user(self, credential: Credential) -> bool: ...
    def reserve_attempt(self, username: str, now: float) -> bool: ...
    def clear_attempts(self, username: str) -> None: ...
    def save_session(self, digest: str, user_id: str, expires: float, now: float) -> None: ...
    def session_user(self, digest: str, now: float) -> LocalUser | None: ...
    def revoke_session(self, digest: str) -> None: ...
