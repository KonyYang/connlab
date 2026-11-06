from pathlib import Path
from types import SimpleNamespace
import runpy
from sqlalchemy import text
from backend.api.main import app
from backend.api.dependencies import get_fee_evaluation_template_resource_store


def test_planning_fee_export_import_roundtrip_without_project_writes(tmp_path):
    fixture = runpy.run_path(str(Path(__file__).with_name('test_matrix_editor_session_api.py')))
    example = runpy.run_path(str(Path(__file__).parents[1] / 'unit/test_tools_matrix_planning.py'))
    workbook = runpy.run_path(str(Path(__file__).parents[1] / 'unit/test_fee_evaluation_workbook_gateway.py'))
    client, engine, _ = fixture['_client'](tmp_path)
    template = tmp_path / 'FDQF-E-176 Fee Evaluation.xlsx'
    workbook['_write_native_xlsx_template'](template)
    # Fixture's labels match the supported Testing Prices contract.
    from openpyxl import load_workbook
    book = load_workbook(template)
    book['Testing Prices'].unmerge_cells('D4:E4')
    for i,value in enumerate(['Group','Man-hour','Description','Unit price','Unit Type','Units','Base fee','Discount','Testing fee'],1):
        book['Testing Prices'].cell(4,i).value=value
    book.save(template); book.close()
    before_template = template.read_bytes()
    app.dependency_overrides[get_fee_evaluation_template_resource_store] = lambda: SimpleNamespace(
        get_by_type=lambda _:SimpleNamespace(path=tmp_path,active=True))
    try:
        with engine.connect() as connection:
            before = connection.execute(text('select count(*) from projects')).scalar()
        matrix = example['matrix']()
        response = client.post('/api/tools/matrix/fees',json=matrix)
        assert response.status_code == 200, response.text
        line=response.json()['groups'][0]['line_items'][0]
        values={'rows':[{'source_line_id':line['line_id']+':1:0','confirmed_group_id':'g1','confirmed_row_id':'r1',
                        'step_token':'1','step_index':0,'spend_time':'2','unit_price':'3','unit_type':'per reading',
                        'units':'10','base_fee':'0','discount':'0','testing_fee':'30','notes':'manual estimate'}],
                'summary':{'condition_confirmation_spend_time':'0','external_cost':'0','external_cost_note':'',
                           'lab_manpower_hourly_rate':'200'}}
        exported=client.post('/api/tools/matrix/fees/export',json={'matrix':matrix,'values':values})
        assert exported.status_code == 200, exported.text[:1000]
        imported=client.post('/api/tools/matrix/fees/import',files={'file':('planning.xlsx',exported.content)})
        assert imported.status_code == 200, imported.text
        result=next(row for row in imported.json()['rows'] if row['rowKind']=='matrix_step')
        assert result['values']['unitPrice']=='3'
        assert result['values']['units']=='10'
        assert template.read_bytes()==before_template
        with engine.connect() as connection:
            assert connection.execute(text('select count(*) from projects')).scalar()==before
    finally:
        app.dependency_overrides.clear(); engine.dispose()


def test_legacy_recovery_reads_saved_matrix_without_writing_any_database_table(tmp_path):
    import sqlite3
    from backend.api.dependencies import get_project_registry_summary_service
    fixture=runpy.run_path(str(Path(__file__).with_name('test_matrix_editor_session_api.py')))
    client,engine,_=fixture['_client'](tmp_path)
    fixture['_seed_project']('P1',tmp_path)
    source_id=fixture['_seed_source_import']('P1',tmp_path)
    try:
        created=client.post('/api/projects/P1/matrix-drafts',json={'source_import_id':source_id,'selected_group_keys':['g1']})
        assert created.status_code==201,created.text
        seed=client.get('/api/projects/P1/matrix-editor/session').json()
        draft=seed['editor_draft']
        draft['rows'][0]['requirement']='Retained manual edit'
        saved=client.put('/api/projects/P1/matrix-editor/session/draft',json={**draft,
            'source_import_id':seed['editor_source_import_id'],'source_snapshot_id':seed['editor_source_snapshot_id']})
        assert saved.status_code==200,saved.text
        # Mark only this isolated fixture as legacy; recovery still reads the real repositories.
        app.dependency_overrides[get_project_registry_summary_service]=lambda:SimpleNamespace(
            get_row=lambda _:SimpleNamespace(display_project_id_kind='temporary'))
        def dump():
            with sqlite3.connect(tmp_path/'connlab.sqlite3') as connection:
                return tuple(connection.iterdump())
        before=dump()
        response=client.get('/api/tools/matrix/legacy/P1')
        assert response.status_code==200,response.text
        assert response.json()['seed']['editor_draft']['rows'][0]['requirement']=='Retained manual edit'
        assert response.json()['fee_values'] is None
        assert dump()==before
    finally:
        app.dependency_overrides.clear();engine.dispose()


def test_materials_api_real_dependencies_copy_originals_without_mutating_intake(tmp_path):
    import sqlite3
    from backend.domain import IntakePackage,IntakeAsset,ExternalResource,ExternalResourceType,IntakePackageSourceType,IntakePackageStatus
    from backend.infrastructure.storage.repositories.intake_package import IntakePackageRepository,IntakeAssetRepository
    from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository
    fixture=runpy.run_path(str(Path(__file__).with_name('test_matrix_editor_session_api.py')))
    client,engine,sessions=fixture['_client'](tmp_path)
    mail=tmp_path/'original.msg';mail.write_bytes(b'original MSG')
    document=tmp_path/'original.docx';document.write_bytes(b'original application')
    root=tmp_path/'materials';root.mkdir()
    try:
        with sessions() as session:
            IntakePackageRepository(session).create(IntakePackage('package',IntakePackageSourceType.OUTLOOK_MSG,
                IntakePackageStatus.DRAFT_SAVED,'mail.msg',mail,subject='客户测试资料',notes='Retained draft'))
            IntakeAssetRepository(session).create(IntakeAsset('asset','package','Application.docx',document,'.docx',None,20,'hash'))
            ExternalResourceRepository(session).upsert(ExternalResource('materials',ExternalResourceType.TEMPORARY_MATERIALS_ROOT,root))
            session.commit()
        def dump():
            with sqlite3.connect(tmp_path/'connlab.sqlite3') as connection:return tuple(connection.iterdump())
        before=dump()
        preview=client.get('/api/intake/packages/package/materials')
        assert preview.status_code==200,preview.text
        assert preview.json()['folder_name']=='客户测试资料'
        assert preview.json()['files']==['mail.msg','Application.docx']
        saved=client.post('/api/intake/packages/package/materials',json={'folder_name':'客户测试资料'})
        assert saved.status_code==200,saved.text
        assert (root/'客户测试资料'/'mail.msg').read_bytes()==mail.read_bytes()
        assert (root/'客户测试资料'/'Application.docx').read_bytes()==document.read_bytes()
        conflict=client.post('/api/intake/packages/package/materials',json={'folder_name':'客户测试资料'})
        assert conflict.status_code==409
        assert dump()==before
    finally:
        app.dependency_overrides.clear();engine.dispose()


def test_tools_matrix_xlsx_export_reimport_prepare_does_not_create_project_records(tmp_path):
    from dataclasses import asdict
    import sqlite3
    from backend.infrastructure.office.connlab_matrix_xlsx_gateway import ConnLabMatrixXlsxGateway
    fixture=runpy.run_path(str(Path(__file__).with_name('test_matrix_editor_session_api.py')))
    example=runpy.run_path(str(Path(__file__).with_name('test_matrix_editor_live_xlsx_export_api.py')))
    client,engine,_=fixture['_client'](tmp_path)
    try:
        with sqlite3.connect(tmp_path/'connlab.sqlite3') as connection:before=tuple(connection.iterdump())
        response=client.post('/api/tools/matrix/export',json=example['payload']())
        assert response.status_code==200,response.text
        downloaded=tmp_path/'Planning.xlsx';downloaded.write_bytes(response.content)
        parsed=ConnLabMatrixXlsxGateway().read(downloaded)
        assert not parsed.blockers
        payload={**asdict(parsed),'source_document_path':str(downloaded),'source_document_name':downloaded.name,'source_format':'.xlsx'}
        prepared=client.post('/api/tools/matrix/prepare',json={'preview_payload':payload})
        assert prepared.status_code==200,prepared.text
        result=prepared.json()['project_matrix_draft']
        assert result['record']['project_id']==''
        assert result['rows'][0]['test_item']=='Item'
        assert result['groups'][0]['sample_quantity_expression']=='5'
        with sqlite3.connect(tmp_path/'connlab.sqlite3') as connection:assert tuple(connection.iterdump())==before
    finally:
        app.dependency_overrides.clear();engine.dispose()
