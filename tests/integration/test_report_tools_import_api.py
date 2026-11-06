"""Tools decisions cross into Report without losing origin or changing authority."""
from tests.integration.test_report_authoring_api import lab, BASE
from tests.unit.test_report_tools_package import service, temperature_input


def package_upload(lab):
    raw, request = temperature_input()
    request['report_metadata']['ltr_number'] = 'DL-2026-05-001'
    name, content = service().export_temperature(raw, 'scanner.csv', request)
    response = lab['client'].post(BASE + '/sources', data={'role': 'tools_result_package', 'expected_revision': 0},
        files={'file': (name, content)})
    assert response.status_code == 200, response.text
    return response.json(), content


def test_tools_temperature_preview_and_confirm_reuse_columns_and_effective_coefficients(lab):
    state, content = package_upload(lab)
    source = state['sources'][-1]
    overview = lab['client'].get(BASE + '/sources/' + source['source_id'] + '/package')
    assert overview.status_code == 200, overview.text
    assert 'content' not in overview.text
    entry = overview.json()['entries'][0]
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'source_id': source['source_id'], 'kind': 'temperature',
        'package_entry_id': entry['entry_id'], **{key: step[key] for key in ('group_id', 'row_id', 'step_token')}}
    preview = lab['client'].post(BASE + '/results/preview', json=request)
    assert preview.status_code == 200, preview.text
    assert preview.json()['data']['effective_maximum_coefficients'] == {'a': 0.0005, 'b': 0.01, 'c': 0}
    assert preview.json()['data']['analysis']['points'][-1]['maximum'] == 24
    assert preview.json()['data']['selection']['temperature_columns'] == [3, 4]
    confirmed = lab['client'].post(BASE + '/results/confirm', json={**request, 'preview_sha256': preview.json()['preview_sha256']})
    assert confirmed.status_code == 200, confirmed.text
    assert lab['client'].get(BASE).json()['results'][-1]['source_sha256'] == source['sha256']
    assert lab['client'].get(source['download_url']).content == content
    assert confirmed.json()['outputs'] == []
    assert confirmed.json()['results'][-1]['outcome'] == 'pending'


def test_package_cannot_select_another_kind_or_unlisted_entry(lab):
    state, _ = package_upload(lab)
    step = state['context']['steps'][0]
    request = {'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id'], 'kind': 'mechanical',
        'package_entry_id': 'temperature', **{key: step[key] for key in ('group_id', 'row_id', 'step_token')}}
    assert lab['client'].post(BASE + '/results/preview', json=request).status_code == 422
    request.update(kind='temperature', package_entry_id='missing')
    assert lab['client'].post(BASE + '/results/preview', json=request).status_code == 422
    assert lab['client'].get(BASE).json()['results'] == []


def test_package_project_and_missing_sample_decisions_are_not_guessed(lab):
    raw, request = temperature_input()  # Deliberately identifies another LTR.
    name, content = service().export_temperature(raw, 'scanner.csv', request)
    response = lab['client'].post(BASE + '/sources', data={'role': 'tools_result_package', 'expected_revision': 0},
        files={'file': (name, content)})
    assert response.status_code == 200, response.text
    state = response.json()
    step = state['context']['steps'][0]
    payload = {'expected_revision': state['revision'], 'source_id': state['sources'][-1]['source_id'],
        'kind': 'temperature', 'package_entry_id': 'temperature',
        **{key: step[key] for key in ('group_id', 'row_id', 'step_token')}}
    rejected = lab['client'].post(BASE + '/results/preview', json=payload)
    assert rejected.status_code == 422 and 'another LTR' in rejected.json()['detail']
    accepted = lab['client'].post(BASE + '/results/preview', json={**payload, 'source_project_confirmed': True})
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()['data']['sample_ids'] == []
    assert accepted.json()['outcome'] == 'pending'
    invalid = lab['client'].post(BASE + '/results/preview', json={**payload,
        'source_project_confirmed': True, 'sample_ids': ['SN1']})
    assert invalid.status_code == 422 and 'channel groups' in invalid.json()['detail']
    assert lab['client'].get(BASE).json()['results'] == []
