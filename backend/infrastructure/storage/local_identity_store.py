"""Separate SQLite store for local credentials, sessions and bounded attempt windows."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from backend.domain.local_identity import Credential, LocalUser, LocalProfile


class LocalIdentityStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute('BEGIN IMMEDIATE')
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            expected = {
                'users': [('user_id', 'TEXT'), ('username', 'TEXT'), ('display_name', 'TEXT'), ('salt', 'BLOB'), ('password_hash', 'BLOB')],
                'sessions': [('digest', 'TEXT'), ('user_id', 'TEXT'), ('expires', 'REAL')],
                'attempts': [('key', 'TEXT'), ('started', 'REAL'), ('count', 'INTEGER')],
            }
            if tables:
                if version != 1 or tables != set(expected) or any(
                    [(row[1], row[2]) for row in connection.execute(f'PRAGMA table_info({table})')] != columns
                    for table, columns in expected.items()
                ) or not self._owned_constraints(connection):
                    raise RuntimeError('The local identity database has an unsupported schema. Preserve it and contact support.')
            elif version != 0:
                raise RuntimeError('The local identity database version is unsupported. Preserve it and contact support.')
            else:
                for statement in (
                    'CREATE TABLE users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, display_name TEXT NOT NULL, salt BLOB NOT NULL, password_hash BLOB NOT NULL)',
                    'CREATE TABLE sessions (digest TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id), expires REAL NOT NULL)',
                    'CREATE TABLE attempts (key TEXT PRIMARY KEY, started REAL NOT NULL, count INTEGER NOT NULL)',
                ):
                    connection.execute(statement)
                connection.execute('PRAGMA user_version=1')

    @staticmethod
    def _owned_constraints(connection) -> bool:
        for table, primary in (('users', 'user_id'), ('sessions', 'digest'), ('attempts', 'key')):
            columns = connection.execute(f'PRAGMA table_info({table})').fetchall()
            if [(row[1], row[5]) for row in columns if row[5]] != [(primary, 1)]:
                return False
            if any(not row[3] for row in columns if row[1] != primary):
                return False
        unique_username = False
        for index in connection.execute('PRAGMA index_list(users)').fetchall():
            if index[2]:
                quoted = index[1].replace('"', '""')
                if [row[2] for row in connection.execute(f'PRAGMA index_info("{quoted}")')] == ['username']:
                    unique_username = True
        foreign = connection.execute('PRAGMA foreign_key_list(sessions)').fetchall()
        return unique_username and any(row[2:5] == ('users', 'user_id', 'user_id') for row in foreign)

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute('PRAGMA foreign_keys=ON')
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def credential(self, username: str) -> Credential | None:
        with self._connection() as connection:
            row = connection.execute('SELECT user_id, username, display_name, salt, password_hash FROM users WHERE username=?', (username,)).fetchone()
        return Credential(LocalUser(*row[:3]), row[3], row[4]) if row else None

    def create_user(self, credential: Credential) -> bool:
        try:
            with self._connection() as connection:
                connection.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)',
                                   (credential.user.user_id, credential.user.username, credential.user.display_name,
                                    credential.salt, credential.password_hash))
            return True
        except sqlite3.IntegrityError:
            return False

    def reserve_attempt(self, username: str, now: float) -> bool:
        # Reserve before expensive hashing; BEGIN IMMEDIATE serializes concurrent attempts.
        with self._connection() as connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute('DELETE FROM attempts WHERE started<=?', (now - 900,))
            for key, seconds, limit in (('global', 60, 40), ('user:' + username, 900, 5)):
                row = connection.execute('SELECT started, count FROM attempts WHERE key=?', (key,)).fetchone()
                if row and now - row[0] < seconds and row[1] >= limit:
                    return False
            for key, seconds in (('global', 60), ('user:' + username, 900)):
                row = connection.execute('SELECT started, count FROM attempts WHERE key=?', (key,)).fetchone()
                started, count = (row[0], row[1] + 1) if row and now - row[0] < seconds else (now, 1)
                connection.execute('INSERT OR REPLACE INTO attempts VALUES (?, ?, ?)', (key, started, count))
            return True

    def clear_attempts(self, username: str) -> None:
        with self._connection() as connection:
            connection.execute('DELETE FROM attempts WHERE key=?', ('user:' + username,))

    def save_session(self, digest: str, user_id: str, expires: float, now: float) -> None:
        with self._connection() as connection:
            connection.execute('DELETE FROM sessions WHERE expires<=?', (now,))
            connection.execute('INSERT INTO sessions VALUES (?, ?, ?)', (digest, user_id, expires))

    def session_user(self, digest: str, now: float) -> LocalUser | None:
        with self._connection() as connection:
            row = connection.execute('SELECT u.user_id, u.username, u.display_name FROM sessions s JOIN users u ON s.user_id=u.user_id WHERE s.digest=? AND s.expires>?', (digest, now)).fetchone()
        return LocalUser(*row) if row else None

    def revoke_session(self, digest: str) -> None:
        with self._connection() as connection:
            connection.execute('DELETE FROM sessions WHERE digest=?', (digest,))


class LocalProfileStore:
    """An independent singleton profile; never opens or migrates registered accounts."""
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute('BEGIN IMMEDIATE')
            objects = connection.execute("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            if objects:
                columns = connection.execute('PRAGMA table_info(profile)').fetchall()
                sql = ''.join(objects[0][2].lower().split()) if len(objects) == 1 and objects[0][2] else ''
                if (version != 1 or len(objects) != 1 or objects[0][:2] != ('table', 'profile')
                        or [(row[1], row[2], row[3], row[5]) for row in columns] != [('id', 'INTEGER', 0, 1), ('display_name', 'TEXT', 1, 0)]
                        or 'check(id=1)' not in sql or 'check(length(trim(display_name))between1and80)' not in sql):
                    raise RuntimeError('本机姓名设置数据库格式不兼容，请保留原文件并联系支持人员。')
            elif version != 0:
                raise RuntimeError('本机姓名设置数据库版本不兼容，请保留原文件并联系支持人员。')
            else:
                connection.execute('CREATE TABLE profile (id INTEGER PRIMARY KEY CHECK(id=1), display_name TEXT NOT NULL CHECK(length(trim(display_name)) BETWEEN 1 AND 80))')
                connection.execute('PRAGMA user_version=1')

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def profile(self) -> LocalProfile | None:
        with self._connection() as connection:
            row = connection.execute('SELECT display_name FROM profile WHERE id=1').fetchone()
        return LocalProfile(row[0]) if row else None

    def save_profile(self, profile: LocalProfile) -> None:
        with self._connection() as connection:
            connection.execute('INSERT INTO profile VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name', (profile.display_name,))
