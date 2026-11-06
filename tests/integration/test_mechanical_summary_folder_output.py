from io import BytesIO
from hashlib import sha256
import pytest
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
from PIL import Image as PILImage
from backend.infrastructure.files.mechanical_summary_folder import analyze_folder
from backend.application.mechanical_summary_folder import apply_review
from backend.infrastructure.office.mechanical_summary_folder import generate_folder_workbook
from tests.unit.test_mechanical_summary_folder import pdf


@pytest.mark.office_integration
def test_folder_workbook_preserves_raw_values_curve_and_approved_report_style():
    book = Workbook(); s = book.active
    for cell, value in {'A1':'Unneeded company', 'D8':'Max', 'E8':'Max', 'D9':'[N]', 'E9':'[mm]',
                        'A13':'1', 'D13':' 105.13', 'E13':' 12.627', 'A15':'Maxi', 'D15':'105.13', 'E15':'=VALUE(E13)'}.items():
        s[cell] = value
    png = BytesIO(); PILImage.new('RGB',(300,200),'blue').save(png,'PNG'); png.seek(0)
    s.add_image(Image(png),'G15')
    out=BytesIO(); book.save(out); book.close()
    sources=[('DL-2026-09-031 polarisation.xlsx',out.getvalue()),
             ('DL-2026-09-031 retention.pdf',pdf(['DL-2026-09-031', 'Retention Force', 'Sample ID Fmax',
                                                 '1 #1-Orange 2930 7.0','2 #1-Black 2760 12.4']))]
    originals=[sha256(data).hexdigest() for _,data in sources]
    analysis=analyze_folder(sources); section=analysis['sections'][0]
    table={'title':'Polarisation','row_heading':'Receptacle','column_heading':'Header','columns':['#1'],
           'samples':['#1'],'results':[['Pass']],'diagonal':True,'curves':['1']}
    ready=apply_review(analysis,{'project':analysis['project'],'sections':{
        section['id']:{'tables':[table],'qualitative_confirmed':True}}})
    result=generate_folder_workbook(sources,ready)
    b=load_workbook(BytesIO(result),data_only=False)
    try:
        s=b['Polarisation & Mis-mating']
        values=[c.value for row in s for c in row]
        assert 'Unneeded company' not in values
        assert ' 105.13' in values
        assert s['E15'].value == '=VALUE(E13)'
        assert s['E15'].data_type == 'f'
        assert len(s._images)==1
        assert values.count('Pass')==1
        assert len([v for v in values if v=='Not recorded'])>=4
        q=b['Contact Retention']
        assert q['H5'].value=='Curve'
        assert q['I5'].value=='SN'
        assert q['J5'].value=='Colour'
        assert q['K6'].value==2930
        assert q['K8'].value=='=MIN(K6:K7)'
        assert q['K11'].value=='=STDEV(K6:K7)'
        assert 'I6:I7' in str(q.merged_cells)
        assert q['H6'].border.left.style is None
        assert q['I5'].fill.fgColor.rgb[-6:]=='BFBFBF'
        assert q['K8'].fill.fgColor.rgb[-6:]=='DAEEF3'
        assert q['I5'].font.name=='Arial'
        assert len(q._images)==1
        assert len(b.worksheets)==2
    finally:
        b.close()
    assert [sha256(data).hexdigest() for _,data in sources]==originals


def test_folder_preview_requests_only_unresolved_correspondence():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_tools_mechanical_summary import router
    app=FastAPI(); app.include_router(router)
    source=pdf(['DL-2026-09-032','MF UMF Fmax','72 1 107 -310 107 15.2'])
    client=TestClient(app)
    response=client.post('/api/tools/mechanical-summary/folder/preview',
        files=[('files',('Test results/mating.pdf',source,'application/pdf'))])
    assert response.status_code==200, response.text
    assert response.json()['ready'] is False
    assert response.json()['sections'][0]['rows'][0]['sample']==''
    rejected=client.post('/api/tools/mechanical-summary/folder/generate',
        files=[('files',('Test results/mating.pdf',source,'application/pdf'))])
    assert rejected.status_code==422


@pytest.mark.office_integration
def test_complete_folder_api_returns_named_editable_workbook():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.api.routes_tools_mechanical_summary import router
    app=FastAPI();app.include_router(router)
    content=pdf(['DL-2026-09-031','Retention Force','Fmax','1 #1 2890 11.6','2 #2 2970 11.5','n = 2'])
    response=TestClient(app).post('/api/tools/mechanical-summary/folder/generate',
        files=[('files',('DL-2026-09-031 retention.pdf',content,'application/pdf'))])
    assert response.status_code==200,response.text
    assert 'DL-2026-09-031 Mechanical Force Summary_' in response.headers['content-disposition']
    book=load_workbook(BytesIO(response.content),data_only=True)
    try:
        assert book['Contact Retention']['J8'].value==2890
        assert book['Contact Retention']['J10'].value==2930
    finally:book.close()
