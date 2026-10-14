from backend.application.local_identity_service import LocalIdentityService, IdentityError
from backend.infrastructure.storage.local_identity_store import LocalIdentityStore
import pytest


def test_login_free_profile_persists_without_touching_registered_credentials(tmp_path):
    from backend.application.local_identity_service import LocalProfileService
    from backend.infrastructure.storage.local_identity_store import LocalProfileStore
    credential_path = tmp_path / 'local_identity.sqlite3'
    LocalIdentityService(LocalIdentityStore(credential_path)).register('alice', 'Alice', 'long password 123')
    original = credential_path.read_bytes()
    service = LocalProfileService(LocalProfileStore(tmp_path / 'local_profile.sqlite3'))
    assert service.profile() is None
    assert service.save('  张 三  ').display_name == '张 三'
    restarted = LocalProfileService(LocalProfileStore(tmp_path / 'local_profile.sqlite3'))
    assert restarted.profile().display_name == '张 三'
    assert credential_path.read_bytes() == original
    for invalid in ('', '   ', '\x00Alice', 'x' * 81):
        with pytest.raises(IdentityError):
            service.save(invalid)
    assert restarted.profile().display_name == '张 三'


def test_registration_login_expiry_and_revocation_survive_restart(tmp_path):
    now = [1000.0]
    store = LocalIdentityStore(tmp_path / 'identity.sqlite3')
    service = LocalIdentityService(store, clock=lambda: now[0])
    session = service.register('alice', 'Alice', 'long password 123', True)
    assert session.user.display_name == 'Alice'
    restarted = LocalIdentityService(LocalIdentityStore(tmp_path / 'identity.sqlite3'), clock=lambda: now[0])
    assert restarted.session(session.token) == session.user
    restarted.logout(session.token)
    assert service.session(session.token) is None
    login = service.login('ALICE', 'long password 123', False)
    now[0] += 8 * 60 * 60 + 1
    assert service.session(login.token) is None


def test_failed_logins_are_bounded_and_registration_is_unique(tmp_path):
    now = [1000.0]
    service = LocalIdentityService(LocalIdentityStore(tmp_path / 'identity.sqlite3'), clock=lambda: now[0])
    service.register('alice', 'Alice', 'long password 123', True)
    for _ in range(5):
        with pytest.raises(IdentityError) as error:
            service.login('alice', 'wrong password', True)
        assert error.value.status == 401
    with pytest.raises(IdentityError) as error:
        service.login('alice', 'long password 123', True)
    assert error.value.status == 429
    now[0] += 901
    assert service.login('alice', 'long password 123', True).user.username == 'alice'
    with pytest.raises(IdentityError):
        service.register('ALICE', 'Other', 'other password 123', True)
