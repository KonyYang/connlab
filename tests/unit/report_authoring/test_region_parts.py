from backend.infrastructure.office.report_authoring.region_parts import remove_replaced_region_parts


def test_removed_unique_curve_is_pruned_but_shared_setup_media_is_retained():
    document = b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body><w:drawing r:embed="setup"/></w:body></w:document>'
    rels = b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="setup" Type="image" Target="media/setup.png"/><Relationship Id="curve" Type="image" Target="media/curve.png"/><Relationship Id="shared" Type="image" Target="media/setup.png"/></Relationships>'
    parts = {'word/document.xml': document, 'word/_rels/document.xml.rels': rels,
        'word/media/setup.png': b'setup', 'word/media/curve.png': b'old curve', 'word/media/unrelated.png': b'unrelated'}
    output = remove_replaced_region_parts(parts, {'curve', 'shared'})
    assert 'word/media/curve.png' not in output
    assert output['word/media/setup.png'] == b'setup'
    assert output['word/media/unrelated.png'] == b'unrelated'
    assert b'Id="curve"' not in output['word/_rels/document.xml.rels']
    assert b'Id="setup"' in output['word/_rels/document.xml.rels']
