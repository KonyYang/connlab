from dataclasses import replace
from pathlib import Path
import sqlite3
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from backend.shared.config import Settings

def settings_for(root, environment="development"):
    root.mkdir(parents=True,exist_ok=True)
    path=root/"connlab.sqlite3"
    with sqlite3.connect(path) as c:c.execute("create table if not exists example(value text)")
    c.close()
    return Settings(data_dir=root,projects_dir=root/"output",templates_dir=root/"templates",database_path=path,environment=environment)

def test_same_database_restart_and_writes_keep_binding_replacement_invalidates_it(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding, RuntimeChanged
    settings=settings_for(portable_tmp_path)
    first=RuntimeBinding(settings)
    with sqlite3.connect(settings.database_path) as c:c.execute("insert into example values ('saved')")
    c.close()
    assert RuntimeBinding(settings).instance_id == first.instance_id
    other=settings.database_path.with_suffix('.new')
    with sqlite3.connect(other) as c:c.execute("create table different(value text)")
    c.close()
    other.replace(settings.database_path)
    with pytest.raises(RuntimeChanged):first.metadata()
    assert RuntimeBinding(settings).instance_id != first.instance_id

def test_same_physical_database_is_namespaced_by_explicit_environment(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding
    settings=settings_for(portable_tmp_path)
    assert RuntimeBinding(settings).instance_id != RuntimeBinding(replace(settings,environment="release")).instance_id

def test_wrong_backend_is_rejected_before_upload_or_draft_handler(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding, install_runtime_binding
    first=RuntimeBinding(settings_for(portable_tmp_path/"dev"))
    second=RuntimeBinding(settings_for(portable_tmp_path/"release", "release"))
    app=FastAPI();install_runtime_binding(app,lambda:second)
    writes=[]
    @app.post('/api/upload')
    async def upload(request:Request):
        writes.append(await request.body());return {"ok":True}
    client=TestClient(app)
    response=client.post('/api/upload',content=b'private draft',headers={"X-ConnLab-Instance":first.instance_id})
    assert response.status_code == 409
    assert writes == []
    response=client.post('/api/upload',content=b'own draft',headers={"X-ConnLab-Instance":second.instance_id})
    assert response.status_code == 200
    assert writes == [b'own draft']
    assert response.headers['X-ConnLab-Instance'] == second.instance_id


def test_native_resource_download_url_also_rejects_wrong_instance(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding,install_runtime_binding
    first=RuntimeBinding(settings_for(portable_tmp_path/"one"))
    second=RuntimeBinding(settings_for(portable_tmp_path/"two","release"))
    app=FastAPI();install_runtime_binding(app,lambda:second)
    @app.get('/api/files/source')
    def download():return {"contents":"release only"}
    client=TestClient(app)
    assert client.get('/api/files/source',params={"connlab_instance":first.instance_id}).status_code==409
    result=client.get('/api/files/source',params={"connlab_instance":second.instance_id})
    assert result.status_code==200 and result.headers["cache-control"]=="no-store"


def test_same_host_cookies_and_profiles_belong_to_each_bound_data_instance(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding,install_runtime_binding
    from backend.api.routes_local_identity import router,get_identity_service,get_profile_service
    from backend.application.local_identity_service import LocalIdentityService,LocalProfileService
    from backend.infrastructure.storage.local_identity_store import LocalIdentityStore,LocalProfileStore
    clients=[]
    for mode in ["development","release"]:
        config=settings_for(portable_tmp_path/mode,mode);binding=RuntimeBinding(config)
        app=FastAPI();app.include_router(router);install_runtime_binding(app,lambda binding=binding:binding)
        app.dependency_overrides[get_identity_service]=lambda config=config:LocalIdentityService(LocalIdentityStore(config.data_dir/"identity.sqlite3"))
        app.dependency_overrides[get_profile_service]=lambda config=config:LocalProfileService(LocalProfileStore(config.data_dir/"profile.sqlite3"))
        client=TestClient(app,base_url="http://localhost",client=("127.0.0.1",50000))
        headers={"Origin":"http://localhost","X-ConnLab-Identity":"1","X-ConnLab-Instance":binding.instance_id}
        response=client.post('/api/local-identity/register',headers=headers,json={"username":"operator","display_name":mode,"password":"test-password-123","remember":True})
        assert response.status_code==200,response.text
        clients.append((client,headers,response.headers['set-cookie'].split('=')[0]))
    assert clients[0][2]!=clients[1][2]
    clients[0][0].cookies.update(clients[1][0].cookies)
    clients[1][0].cookies.update(clients[0][0].cookies)
    for (client,headers,_),mode in zip(clients,["development","release"]):
        assert client.get('/api/local-identity/session',headers=headers).json()['user']['display_name']==mode


def test_runtime_reports_the_same_existing_project_location_as_first_use(portable_tmp_path):
    from backend.api.runtime_binding import RuntimeBinding
    from backend.application.default_storage_locations import DefaultStorageLocations
    settings=replace(settings_for(portable_tmp_path),projects_dir=portable_tmp_path/"operator-chosen/Projects",projects_directory_explicit=True)
    class Resources:
        def get_by_type(self,kind): return None
    from backend.domain import ExternalResourceType
    locations=DefaultStorageLocations(settings,Resources(),None)
    assert RuntimeBinding(settings).metadata()["default_output_paths"]["Projects"]==str(locations.effective(ExternalResourceType.PROJECT_OUTPUT_ROOT))
    assert not settings.projects_dir.exists()
