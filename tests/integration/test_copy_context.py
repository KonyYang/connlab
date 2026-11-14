"""Live copy contexts are isolated per browser session and never persisted as project data."""
import pytest


def test_context_clear_and_out_of_order_activation_cannot_resurrect_old_target():
    from backend.application.project_library.copy_context import CopyContextRegistry
    contexts = CopyContextRegistry()
    session = contexts.create()['session_id']
    first = contexts.update(session, 1, lambda: {'key':'project:p1','project_id':'p1','folder_path':'root'})
    with contexts.guard({'session_id':session,'token':first['token']}) as active:
        assert active['target']['key'] == 'project:p1'
    contexts.update(session, 3, lambda: None)
    with pytest.raises(ValueError, match='changed'):
        contexts.update(session, 2, lambda: {'key':'project:p1'})
    with pytest.raises(ValueError, match='Workbench'):
        with contexts.guard({'session_id':session,'token':first['token']}):
            pytest.fail('cleared context must not be usable')
    other = contexts.create()['session_id']
    second = contexts.update(session, 4, lambda: {'key':'project:p2'})
    with pytest.raises(ValueError):
        with contexts.guard({'session_id':other,'token':second['token']}):
            pytest.fail('session contexts must not leak')


def test_context_clear_is_ordered_after_inflight_publication_guard():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from backend.application.project_library.copy_context import CopyContextRegistry
    contexts=CopyContextRegistry()
    session=contexts.create()['session_id']
    active=contexts.update(session,1,lambda:{'key':'project:p1'})
    proof={'session_id':session,'token':active['token']}
    entered=Event()
    def clear():
        entered.set()
        return contexts.update(session,2,lambda:None)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with contexts.guard(proof):
            future=pool.submit(clear)
            assert entered.wait(2)
            assert not future.done()
        assert future.result(timeout=2)['target'] is None
    with pytest.raises(ValueError):
        with contexts.guard(proof):
            pytest.fail('publication guard must not survive clear')
