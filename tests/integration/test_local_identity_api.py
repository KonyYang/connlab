from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_local_identity import router, get_identity_service, get_profile_service
from backend.application.local_identity_service import LocalIdentityService, LocalProfileService
from backend.infrastructure.storage.local_identity_store import LocalIdentityStore, LocalProfileStore
import pytest
import json


@pytest.fixture
def identity_app(tmp_path):
    app = FastAPI()
    app.include_router(router)
    now = [1000.0]
    app.dependency_overrides[get_identity_service] = lambda: LocalIdentityService(LocalIdentityStore(tmp_path / 'identity.sqlite3'), clock=lambda: now[0])
    return app, now


HEADERS = {'Origin': 'http://localhost:5173', 'X-ConnLab-Identity': '1'}
USER = {'username': 'alice', 'display_name': 'Alice', 'password': 'long password 123'}


def test_login_free_profile_read_save_restart_has_no_cookie_expiry_or_old_database_access(tmp_path):
    app = FastAPI()
    app.include_router(router)
    profile_path = tmp_path / 'local_profile.sqlite3'
    identity_path = tmp_path / 'local_identity.sqlite3'
    LocalIdentityService(LocalIdentityStore(identity_path)).register('alice', 'Alice', 'long password 123')
    old = identity_path.read_bytes()
    app.dependency_overrides[get_profile_service] = lambda: LocalProfileService(LocalProfileStore(profile_path))
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        assert client.get('/api/local-identity/profile').json() == {'profile': None}
        response = client.put('/api/local-identity/profile', json={'display_name': ' 张 三 '}, headers=HEADERS)
        assert response.status_code == 200
        assert response.json() == {'profile': {'display_name': '张 三'}}
        assert 'set-cookie' not in response.headers
        assert response.headers['cache-control'] == 'no-store'
        assert client.put('/api/local-identity/profile', json={'display_name': ''}, headers=HEADERS).json() == {
            'detail': {'field': 'display_name', 'message': '请填写项目负责人姓名。'}}
        assert client.put('/api/local-identity/profile', json={'display_name': 'Other'}, headers={}).status_code == 403
        assert client.put('/api/local-identity/profile', json={'display_name': 'Other'}, headers=HEADERS | {'Origin': 'https://evil.test'}).status_code == 403
        response = client.get('/api/local-identity/profile')
        assert response.json() == {'profile': {'display_name': '张 三'}}
        assert 'set-cookie' not in response.headers
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as restarted:
        assert restarted.get('/api/local-identity/profile').json() == {'profile': {'display_name': '张 三'}}
    assert identity_path.read_bytes() == old


@pytest.mark.parametrize('name', ['', '   ', 1, None, ['Alice'], 'x' * 81, '\x00name', '\ud800'])
def test_profile_name_validation_explains_the_field_without_echoing_invalid_input(tmp_path, name):
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_profile_service] = lambda: LocalProfileService(LocalProfileStore(tmp_path / 'profile.sqlite3'))
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        response = client.put('/api/local-identity/profile', content=json.dumps({'display_name': name}),
                              headers=HEADERS | {'Content-Type': 'application/json'})
        assert response.status_code == 400
        assert response.json()['detail']['field'] == 'display_name'
        assert response.headers['cache-control'] == 'no-store'
        assert client.get('/api/local-identity/profile').json() == {'profile': None}


@pytest.mark.parametrize('patch', [
    {'password': 'short'}, {'password': 123}, {'password': ['secret']}, {'password': 'x' * 129},
    {'username': 'a'}, {'username': None}, {'display_name': ''}, {'display_name': '\x00'}, {'remember': 'true'},
])
def test_invalid_credentials_are_secret_safe(identity_app, patch):
    app, _ = identity_app
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        response = client.post('/api/local-identity/register', json=USER | patch, headers=HEADERS)
        assert response.status_code == 400
        assert 'long password 123' not in response.text
        assert response.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize('headers', [{}, {'Origin': 'http://localhost:5173'}, HEADERS | {'Origin': 'https://evil.test'},
                                    HEADERS | {'Host': 'evil.test'}, HEADERS | {'Content-Type': 'application/x-www-form-urlencoded'}])
def test_identity_mutations_require_exact_local_origin_header_and_json(identity_app, headers):
    app, _ = identity_app
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        response = client.post('/api/local-identity/register', json=USER, headers=headers)
        assert response.status_code in (403, 415)
        assert client.get('/api/local-identity/session').json() == {'user': None}


def test_session_rotation_replay_expiry_and_nonremember_cookie(identity_app):
    app, now = identity_app
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        assert client.post('/api/local-identity/register', json=USER, headers=HEADERS).status_code == 200
        old_token = client.cookies.get('connlab_local_session')
        assert client.post('/api/local-identity/register', json=USER | {'username': 'ALICE'}, headers=HEADERS).status_code == 409
        payload = {'username': 'ALICE', 'password': USER['password'], 'remember': False}
        response = client.post('/api/local-identity/login', json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert 'Max-Age' not in response.headers['set-cookie']
        stale = client.get('/api/local-identity/session', headers={'Cookie': f'connlab_local_session={old_token}'})
        assert stale.json() == {'user': None}
        assert 'set-cookie' not in stale.headers
        assert client.get('/api/local-identity/session').json()['user']['username'] == 'alice'
        now[0] += 8 * 60 * 60 + 1
        expired = client.get('/api/local-identity/session')
        assert expired.json() == {'user': None}
        assert 'set-cookie' not in expired.headers


def test_login_throttling_is_persistent_with_cooldown_and_unknown_users(identity_app):
    app, now = identity_app
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        client.post('/api/local-identity/register', json=USER, headers=HEADERS)
        for _ in range(5):
            response = client.post('/api/local-identity/login', json={'username': 'alice', 'password': 'wrong password'}, headers=HEADERS)
            assert response.status_code == 401
        assert client.post('/api/local-identity/login', json={'username': 'alice', 'password': USER['password']}, headers=HEADERS).status_code == 429
        now[0] += 901
        assert client.post('/api/local-identity/login', json={'username': 'alice', 'password': USER['password']}, headers=HEADERS).status_code == 200
        unknown = client.post('/api/local-identity/login', json={'username': 'unknown', 'password': 'wrong password'}, headers=HEADERS)
        assert unknown.status_code == 401
        assert unknown.json() == {'detail': 'Username or password is incorrect.'}


def test_nonlocal_peer_cannot_use_local_identity_even_with_loopback_host(identity_app):
    app, _ = identity_app
    with TestClient(app, base_url='http://localhost:5173', client=('192.0.2.1', 12345)) as client:
        assert client.post('/api/local-identity/register', json=USER, headers=HEADERS).status_code == 403
        assert client.get('/api/local-identity/session').status_code == 403


def test_registration_cookie_session_logout_and_secret_safe_validation(tmp_path):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_identity_service] = lambda: LocalIdentityService(LocalIdentityStore(tmp_path / 'identity.sqlite3'))
    with TestClient(app, base_url='http://localhost:5173', client=('127.0.0.1', 12345)) as client:
        headers = {'Origin': 'http://localhost:5173', 'X-ConnLab-Identity': '1'}
        payload = {'username': 'alice', 'display_name': 'Alice', 'password': 'long password 123'}
        assert client.post('/api/local-identity/register', json=payload).status_code == 403
        response = client.post('/api/local-identity/register', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['user']['display_name'] == 'Alice'
        cookie = response.headers['set-cookie']
        assert 'HttpOnly' in cookie and 'SameSite=strict' in cookie and 'Max-Age=2592000' in cookie
        assert 'Domain=' not in cookie and 'Path=/api/local-identity' in cookie
        assert client.get('/api/local-identity/session').json()['user']['username'] == 'alice'
        assert client.post('/api/local-identity/logout', json={}, headers=headers).json() == {'user': None}
        assert client.get('/api/local-identity/session').json() == {'user': None}
        secret = 'private-secret' * 100
        response = client.post('/api/local-identity/login', json={'username': 'alice', 'password': secret}, headers=headers)
        assert response.status_code == 400
        assert secret not in response.text
        assert client.post('/api/local-identity/login', json=payload, headers=headers | {'Origin': 'https://evil.test'}).status_code == 403
