"""Windows-safe material folder and filename rules."""
import re

def validate_material_name(name: str) -> str:
    if not name or name != name.strip() or name.endswith('.') or len(name) > 180:
        raise ValueError('Enter a folder name without trailing spaces or dots (up to 180 characters).')
    if name in {'.', '..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]', name):
        raise ValueError('The name contains characters that Windows cannot use.')
    if re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', name.split('.')[0], re.I):
        raise ValueError('This name is reserved by Windows.')
    return name


def suggested_material_name(name: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name).strip().rstrip('.')[:160]
    try:
        return validate_material_name(value)
    except ValueError:
        return 'Request materials'
