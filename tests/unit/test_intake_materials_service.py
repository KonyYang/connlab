from pathlib import Path
from types import SimpleNamespace
import pytest
from backend.application.intake_materials_service import IntakeMaterialsService
from backend.infrastructure.files.materials_copy_gateway import MaterialsCopyGateway

class Store:
    def __init__(self, value): self.value = value
    def get(self, key): return self.value
    def get_by_type(self, key): return self.value
    def list_by_package(self, key): return self.value


def service(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    output = tmp_path / 'output'; output.mkdir()
    mail = source / 'mail.msg'; mail.write_bytes(b'mail-original')
    form = source / 'form.docx'; form.write_bytes(b'form-original')
    package = SimpleNamespace(source_stored_path=mail, source_original_name='request.msg', subject='Qualification request')
    assets = [SimpleNamespace(stored_path=form, original_name='request.docx')]
    return IntakeMaterialsService(Store(package), Store(assets), Store(SimpleNamespace(path=output, active=True)), MaterialsCopyGateway()), output


def test_save_materials_preserves_original_mail_and_attachments(tmp_path):
    app, output = service(tmp_path)
    preview = app.preview('package')
    assert preview['folder_name'] == 'Qualification request'
    saved = app.save('package', 'My request')
    assert Path(saved['path']) == output / 'My request'
    assert (output / 'My request' / 'request.msg').read_bytes() == b'mail-original'
    assert (output / 'My request' / 'request.docx').read_bytes() == b'form-original'
    with pytest.raises(ValueError, match='already exists'):
        app.save('package', 'My request')

@pytest.mark.parametrize('name', ['../outside', 'a/b', 'C:\\outside', 'CON', 'name.', ''])
def test_rejects_unsafe_folder_names(tmp_path, name):
    app, output = service(tmp_path)
    with pytest.raises(ValueError): app.save('package', name)
    assert list(output.iterdir()) == []


def test_unicode_name_and_same_named_attachments_retain_extensions(tmp_path):
    app, output = service(tmp_path)
    app.packages.value.subject = '客户资格测试'
    first = app.assets.value[0]
    first.original_name = '申请单.docx'
    other = first.stored_path.with_name('second.docx'); other.write_bytes(b'second')
    app.assets.value.append(SimpleNamespace(stored_path=other, original_name='申请单.docx'))
    preview = app.preview('package')
    assert preview['folder_name'] == '客户资格测试'
    assert preview['files'] == ['request.msg','申请单.docx','申请单 (2).docx']
    saved=app.save('package',preview['folder_name'])
    assert (Path(saved['path'])/'申请单 (2).docx').read_bytes() == b'second'


def test_copy_failure_preserves_existing_items_and_reports_partial_destination(tmp_path, monkeypatch):
    import backend.infrastructure.files.materials_copy_gateway as gateway
    app, output = service(tmp_path)
    def interrupted(reader, writer):
        writer.write(b'partial')
        (Path(writer.name).parent/'colleague.txt').write_bytes(b'keep')
        raise OSError('disk full')
    monkeypatch.setattr(gateway.shutil,'copyfileobj',interrupted)
    with pytest.raises(ValueError,match='Partial files may remain'):
        app.save('package','New request')
    assert (output/'New request'/'colleague.txt').read_bytes() == b'keep'
    assert (output/'New request'/'request.msg').read_bytes() == b'partial'


def test_missing_root_or_source_never_creates_target(tmp_path):
    app, output = service(tmp_path)
    app.assets.value[0].stored_path.unlink()
    with pytest.raises(ValueError,match='Source file is missing'):
        app.save('package','New request')
    assert list(output.iterdir()) == []
    output.rmdir()
    with pytest.raises(ValueError,match='Materials folder is not available'):
        app.preview('package')
    assert not output.exists()


def test_reparse_directory_is_rejected_before_copy(tmp_path, monkeypatch):
    app, output = service(tmp_path)
    original = Path.lstat
    def stat(path, *args, **kwargs):
        result = original(path,*args,**kwargs)
        if path == output:
            return SimpleNamespace(st_mode=result.st_mode,st_file_attributes=0x400)
        return result
    monkeypatch.setattr(Path,'lstat',stat)
    with pytest.raises(ValueError,match='Redirected folders'):
        app.save('package','New request')
    assert list(output.iterdir()) == []
