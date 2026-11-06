"""Retain request files without creating a Project or changing its Intake draft."""
from pathlib import Path
from backend.domain import ExternalResourceType
from typing import Protocol
from backend.application.material_names import suggested_material_name, validate_material_name

class MaterialsGateway(Protocol):
    def checked_directory(self, path: Path) -> Path: ...
    def save(self, root: Path, name: str, files: list[tuple[Path, str]]) -> Path: ...


class IntakeMaterialsService:
    def __init__(self, packages, assets, resources, copier: MaterialsGateway):
        self.packages, self.assets, self.resources = packages, assets, resources
        self.copier = copier

    def _source(self, package_id):
        package = self.packages.get(package_id)
        if package is None:
            raise ValueError('The imported request is no longer available. Import it again.')
        resource = self.resources.get_by_type(ExternalResourceType.TEMPORARY_MATERIALS_ROOT)
        if resource is None or not resource.active:
            raise ValueError('Set Temporary materials folder in Settings before saving.')
        root = self.copier.checked_directory(resource.path)
        items = [(package.source_stored_path, package.source_original_name)]
        items.extend((asset.stored_path, asset.original_name) for asset in self.assets.list_by_package(package_id))
        files, seen_paths, seen_names = [], set(), set()
        for source, original in items:
            if source.resolve() in seen_paths:
                continue
            if not source.is_file():
                raise ValueError(f'Source file is missing: {original}')
            seen_paths.add(source.resolve())
            suffix = Path(original).suffix
            name = suggested_material_name(Path(original).stem) + suffix
            validate_material_name(name)
            stem, suffix = Path(name).stem, Path(name).suffix
            index = 2
            while name.casefold() in seen_names:
                name = f'{stem} ({index}){suffix}'; index += 1
            seen_names.add(name.casefold())
            files.append((source, name))
        return package, root, files

    def preview(self, package_id):
        package, root, files = self._source(package_id)
        return {'folder_name': suggested_material_name(package.subject or Path(package.source_original_name).stem),
                'root': str(root), 'files': [name for _, name in files]}

    def save(self, package_id, folder_name):
        _, root, files = self._source(package_id)
        path = self.copier.save(root, folder_name, files)
        return {'path': str(path), 'folder_name': folder_name, 'files': [name for _, name in files]}

    def folder(self, folder_name):
        resource = self.resources.get_by_type(ExternalResourceType.TEMPORARY_MATERIALS_ROOT)
        if resource is None or not resource.active:
            raise ValueError('Set Temporary materials folder in Settings.')
        root = self.copier.checked_directory(resource.path)
        return self.copier.checked_directory(root / validate_material_name(folder_name))
