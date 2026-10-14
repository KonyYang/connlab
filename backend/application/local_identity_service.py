"""Local password authentication, independent of project roles and document authority."""
from dataclasses import dataclass
import hashlib
import hmac
import re
import secrets
import time
from typing import Callable

from backend.domain.local_identity import Credential, IdentityStore, LocalUser, LocalProfile, ProfileStore

ITERATIONS = 600_000
REMEMBER_SECONDS = 30 * 24 * 60 * 60
SESSION_SECONDS = 8 * 60 * 60


class LocalProfileService:
    """Persistent report/project defaults, not authentication or an audit identity."""
    def __init__(self, store: ProfileStore):
        self.store = store

    def profile(self) -> LocalProfile | None:
        return self.store.profile()

    def save(self, display_name: str) -> LocalProfile:
        if not isinstance(display_name, str) or not display_name.strip():
            raise IdentityError('请填写项目负责人姓名。')
        if re.search(r'[\x00-\x1f\x7f\ud800-\udfff]', display_name):
            raise IdentityError('姓名不能包含控制字符或无效字符。')
        name = display_name.strip()
        if len(name) > 80:
            raise IdentityError('姓名最多为 80 个字符。')
        profile = LocalProfile(name)
        self.store.save_profile(profile)
        return profile


class IdentityError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class AuthenticatedSession:
    user: LocalUser
    token: str
    max_age: int | None


class LocalIdentityService:
    def __init__(self, store: IdentityStore, clock: Callable[[], float] = time.time):
        self.store = store
        self.clock = clock

    def register(self, username: str, display_name: str, password: str, remember: bool = True,
                 prior_token: str | None = None) -> AuthenticatedSession:
        username = self._username(username)
        self._password(password)
        if not isinstance(display_name, str) or not 1 <= len(display_name.strip()) <= 80 or re.search(r'[\x00-\x1f\x7f]', display_name):
            raise IdentityError('Enter a display name of 1–80 characters.')
        self._attempt(username)
        salt = secrets.token_bytes(16)
        user = LocalUser(secrets.token_hex(16), username, display_name.strip())
        credential = Credential(user, salt, self._hash(password, salt))
        if not self.store.create_user(credential):
            raise IdentityError('This username is already registered.', 409)
        self.store.clear_attempts(username)
        return self._authenticate(user, remember, prior_token)

    def login(self, username: str, password: str, remember: bool = True,
              prior_token: str | None = None) -> AuthenticatedSession:
        username = self._username(username)
        self._password(password)
        self._attempt(username)
        credential = self.store.credential(username)
        # Unknown users pay the same password hashing cost; no cheap enumeration path.
        supplied = self._hash(password, credential.salt if credential else bytes(16))
        expected = credential.password_hash if credential else bytes(32)
        if not hmac.compare_digest(supplied, expected) or credential is None:
            raise IdentityError('Username or password is incorrect.', 401)
        self.store.clear_attempts(username)
        return self._authenticate(credential.user, remember, prior_token)

    def session(self, token: str | None) -> LocalUser | None:
        if not token or not re.fullmatch(r'[A-Za-z0-9_-]{43}', token):
            return None
        return self.store.session_user(self._digest(token), self.clock())

    def logout(self, token: str | None) -> None:
        if token:
            self.store.revoke_session(self._digest(token))

    def _authenticate(self, user: LocalUser, remember: bool, prior: str | None) -> AuthenticatedSession:
        token = secrets.token_urlsafe(32)
        duration = REMEMBER_SECONDS if remember else SESSION_SECONDS
        self.logout(prior)
        self.store.save_session(self._digest(token), user.user_id, self.clock() + duration, self.clock())
        return AuthenticatedSession(user, token, duration if remember else None)

    def _attempt(self, username: str) -> None:
        if not self.store.reserve_attempt(username, self.clock()):
            raise IdentityError('Too many attempts. Please try again later.', 429)

    @staticmethod
    def _username(value: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{3,64}', value):
            raise IdentityError('Use 3–64 letters, digits, dots, underscores or hyphens for the username.')
        return value.lower()

    @staticmethod
    def _password(value: str) -> None:
        if not isinstance(value, str) or not 10 <= len(value) <= 128:
            raise IdentityError('Use a password of 10–128 characters.')

    @staticmethod
    def _hash(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
