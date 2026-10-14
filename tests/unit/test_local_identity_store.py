import sqlite3
import pytest
from concurrent.futures import ThreadPoolExecutor
from backend.application.local_identity_service import LocalIdentityService
from backend.infrastructure.storage.local_identity_store import LocalIdentityStore


def test_persisted_credentials_and_sessions_do_not_store_plain_secrets(tmp_path):
    path = tmp_path / 'identity.sqlite3'
    service = LocalIdentityService(LocalIdentityStore(path))
    result = service.register('alice', 'Alice', 'secret password 123')
    with sqlite3.connect(path) as connection:
        salt, password_hash = connection.execute('SELECT salt, password_hash FROM users').fetchone()
        digest = connection.execute('SELECT digest FROM sessions').fetchone()[0]
    assert len(salt) >= 16 and len(password_hash) == 32
    assert password_hash != b'secret password 123'
    assert digest != result.token
    assert b'secret password 123' not in path.read_bytes()
    assert result.token.encode() not in path.read_bytes()


def test_attempt_reservations_are_atomic_and_globally_bounded(tmp_path):
    store = LocalIdentityStore(tmp_path / 'identity.sqlite3')
    with ThreadPoolExecutor(max_workers=10) as executor:
        same = list(executor.map(lambda _: store.reserve_attempt('alice', 1000), range(10)))
    assert sum(same) == 5
    store.clear_attempts('alice')
    assert sum(store.reserve_attempt(f'user{index}', 1000) for index in range(100)) == 35
    assert store.reserve_attempt('alice', 1901)


def test_unowned_or_incompatible_database_is_rejected_without_modifying_it(tmp_path):
    path = tmp_path / 'identity.sqlite3'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE users (legacy_name TEXT)')
        connection.execute("INSERT INTO users VALUES ('Preserve this data')")
    original = path.read_bytes()
    with pytest.raises(RuntimeError, match='unsupported schema'):
        LocalIdentityStore(path)
    assert path.read_bytes() == original
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [('users',)]


def test_owned_version_with_missing_unique_constraint_is_rejected_unchanged(tmp_path):
    path = tmp_path / 'identity.sqlite3'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE users (user_id TEXT PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, salt BLOB NOT NULL, password_hash BLOB NOT NULL)')
        connection.execute('CREATE TABLE sessions (digest TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id), expires REAL NOT NULL)')
        connection.execute('CREATE TABLE attempts (key TEXT PRIMARY KEY, started REAL NOT NULL, count INTEGER NOT NULL)')
        connection.execute('PRAGMA user_version=1')
    original = path.read_bytes()
    with pytest.raises(RuntimeError, match='unsupported schema'):
        LocalIdentityStore(path)
    assert path.read_bytes() == original
