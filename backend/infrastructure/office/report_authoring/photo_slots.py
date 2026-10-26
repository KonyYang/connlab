"""Occurrence-based DOCX photo replacement without reserializing unrelated package parts."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import posixpath
from zipfile import ZipFile

from lxml import etree
from PIL import Image, ImageOps

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "v": "urn:schemas-microsoft-com:vml",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
}
DOCUMENT = "word/document.xml"
RELS = "word/_rels/document.xml.rels"
TYPES = "[Content_Types].xml"


@dataclass(frozen=True)
class PhotoSlot:
    slot_id: str
    caption: str
    width_emu: int
    height_emu: int
    media_sha256: str | None
    supported: bool
    reason: str | None = None
    rotation: int = 0
    flip_horizontal: bool = False
    flip_vertical: bool = False


@dataclass(frozen=True)
class PhotoReplacement:
    slot_id: str
    content: bytes
    crop_mode: str = "preserve"
    accept_slot_transform: bool = False


@dataclass(frozen=True)
class PhotoUpdateResult:
    changed: bool
    sha256: str
    changed_slots: tuple[str, ...]


def _xml(data: bytes):
    return etree.fromstring(data, parser=etree.XMLParser(resolve_entities=False, no_network=True))


def _package(source: Path):
    raw = Path(source).read_bytes()
    if len(raw) > 60 * 1024 * 1024:
        raise ValueError("Report exceeds the photo-update size limit.")
    with ZipFile(BytesIO(raw)) as archive:
        items = archive.infolist()
        if len(items) > 4000 or sum(item.file_size for item in items) > 200 * 1024 * 1024:
            raise ValueError("Report package is too large to inspect safely.")
        if len({item.filename for item in items}) != len(items):
            raise ValueError("Report contains duplicate package parts.")
        parts = {item.filename: archive.read(item) for item in items}
    return raw, items, parts


def _relationship_target(relationship):
    if relationship is None or relationship.get("TargetMode") == "External":
        return None
    target = posixpath.normpath(posixpath.join("word", relationship.get("Target", "")))
    return target if target.startswith("word/media/") else None


def _caption(node) -> str:
    paragraphs = node.xpath("ancestor::w:p[1]", namespaces=NS)
    if not paragraphs:
        return "Photo"
    paragraph = paragraphs[0]
    for candidate in [paragraph, *list(paragraph.itersiblings())[:3]]:
        if candidate.tag != "{" + NS["w"] + "}p":
            break
        text = "".join(candidate.xpath(".//w:t/text()", namespaces=NS)).strip()
        if text:
            return text[:300]
    properties = node.xpath("ancestor::wp:inline/wp:docPr | ancestor::wp:anchor/wp:docPr", namespaces=NS)
    return (properties[0].get("descr") or properties[0].get("name") or "Photo") if properties else "Photo"


def _slots(parts):
    document = _xml(parts[DOCUMENT])
    relationships = _xml(parts[RELS])
    by_id = {item.get("Id"): item for item in relationships}
    slots = []
    for index, node in enumerate(document.xpath("//a:blip | //v:imagedata", namespaces=NS)):
        if node.xpath("ancestor::w:del | ancestor::w:moveFrom", namespaces=NS):
            continue
        slot_id = f"photo-{index + 1}"
        relationship = by_id.get(node.get("{" + NS["r"] + "}embed") or node.get("{" + NS["r"] + "}id"))
        target = _relationship_target(relationship)
        shapes = node.xpath("ancestor::wp:inline[1] | ancestor::wp:anchor[1]", namespaces=NS)
        shape = shapes[0] if len(shapes) == 1 else None
        extents = shape.find("wp:extent", NS) if shape is not None else None
        reason = None
        if node.tag != "{" + NS["a"] + "}blip" or shape is None:
            reason = "Legacy or unsupported drawing: review this slot manually."
        elif node.xpath("ancestor::wpg:wgp", namespaces=NS):
            reason = "Grouped drawing: replace only after confirming its image/annotation structure."
        elif not target or target not in parts:
            reason = "Linked or missing image: an embedded photo is required."
        xforms = node.xpath("ancestor::pic:pic/pic:spPr/a:xfrm", namespaces=NS)
        xform = xforms[0] if xforms else None
        rotation = int(xform.get("rot", "0")) if xform is not None else 0
        flip_h = xform is not None and xform.get("flipH") in ("1", "true")
        flip_v = xform is not None and xform.get("flipV") in ("1", "true")
        slot = PhotoSlot(slot_id, _caption(node), int(extents.get("cx", 0)) if extents is not None else 0,
            int(extents.get("cy", 0)) if extents is not None else 0,
            sha256(parts[target]).hexdigest() if target and target in parts else None,
            reason is None, reason, rotation, flip_h, flip_v)
        slots.append((slot, node, target))
    return document, relationships, slots


def inspect_photo_slots(source: Path) -> tuple[PhotoSlot, ...]:
    """List body-photo occurrences, not unique media; headers/logos are not candidates."""
    _, _, parts = _package(source)
    return tuple(slot for slot, _, _ in _slots(parts)[2])


def read_photo_slot(source: Path, slot_id: str) -> tuple[bytes, str]:
    _, _, parts = _package(source)
    for slot, _, target in _slots(parts)[2]:
        if slot.slot_id == slot_id:
            if not slot.supported or target is None:
                raise ValueError(slot.reason or "Unsupported photo slot.")
            content = parts[target]
            _, _, mime = _image(content, normalize=False)
            return content, mime
    raise ValueError("Photo slot is no longer present; refresh the report preview.")


def _image(content: bytes, *, normalize: bool):
    if len(content) > 20 * 1024 * 1024:
        raise ValueError("Choose a photo smaller than 20 MB.")
    try:
        with Image.open(BytesIO(content)) as image:
            if image.format not in {"PNG", "JPEG"} or image.width * image.height > 40_000_000:
                raise ValueError("Choose a PNG or JPEG photo of at most 40 megapixels.")
            size = image.size
            mime = "image/png" if image.format == "PNG" else "image/jpeg"
            image.load()
            if normalize and image.getexif().get(274, 1) != 1:
                upright = ImageOps.exif_transpose(image)
                buffer = BytesIO()
                upright.save(buffer, format="PNG")
                return buffer.getvalue(), upright.size, "image/png"
            return content, size, mime
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Photo could not be read safely; choose a PNG or JPEG.") from exc


def _apply_crop(slot, node, old_size, new_size, mode):
    if mode not in {"preserve", "centre_crop"}:
        raise ValueError("Unknown photo crop mode.")
    old_ratio, new_ratio = old_size[0] / old_size[1], new_size[0] / new_size[1]
    if mode == "preserve":
        if abs(new_ratio / old_ratio - 1) > 0.01:
            raise ValueError("Photo proportions differ; choose centre_crop or provide matching proportions.")
        return
    if slot.width_emu <= 0 or slot.height_emu <= 0:
        raise ValueError("Cannot determine the photo frame for crop.")
    frame_ratio = slot.width_emu / slot.height_emu
    # wp:extent is the unrotated frame; the existing transform remains untouched.
    crop = node.getparent().find("a:srcRect", NS)
    if crop is None:
        crop = etree.Element("{" + NS["a"] + "}srcRect")
        node.addnext(crop)
    for edge in ("l", "r", "t", "b"):
        crop.set(edge, "0")
    if new_ratio > frame_ratio:
        amount = round((1 - frame_ratio / new_ratio) * 50000)
        crop.set("l", str(amount)); crop.set("r", str(amount))
    else:
        amount = round((1 - new_ratio / frame_ratio) * 50000)
        crop.set("t", str(amount)); crop.set("b", str(amount))


def replace_photo_slots(source: Path, output: Path, replacements: list[PhotoReplacement], *,
                        expected_source_sha256: str) -> PhotoUpdateResult:
    """Write a new package, retaining unrelated bytes and source; never publish or overwrite."""
    source, output = Path(source), Path(output)
    if output.exists() or output.resolve() == source.resolve():
        raise FileExistsError("Photo update requires a new, independent output path.")
    raw, items, parts = _package(source)
    if sha256(raw).hexdigest() != expected_source_sha256:
        raise ValueError("Report changed; refresh the photo preview.")
    document, relationships, candidates = _slots(parts)
    slots = {slot.slot_id: (slot, node, target) for slot, node, target in candidates}
    if len({item.slot_id for item in replacements}) != len(replacements):
        raise ValueError("Select each photo slot only once.")
    changed = []
    additions = {}
    content_types = _xml(parts[TYPES])
    for replacement in replacements:
        if replacement.slot_id not in slots:
            raise ValueError("Photo slot is no longer present; refresh the report preview.")
        slot, node, target = slots[replacement.slot_id]
        if not slot.supported:
            raise ValueError(slot.reason)
        same_bytes = replacement.content == parts[target]
        if same_bytes and replacement.crop_mode == "preserve":
            continue
        content, new_size, mime = _image(replacement.content, normalize=not same_bytes)
        _, old_size, _ = _image(parts[target], normalize=False)
        previous_fill = etree.tostring(node.getparent())
        _apply_crop(slot, node, old_size, new_size, replacement.crop_mode)
        if content == parts[target] and previous_fill == etree.tostring(node.getparent()):
            continue
        if (slot.rotation or slot.flip_horizontal or slot.flip_vertical) and not replacement.accept_slot_transform:
            raise ValueError("Review and accept the slot rotation/flip before replacing this photo.")
        if content == parts[target]:
            changed.append(slot.slot_id)
            continue
        identity = sha256(slot.slot_id.encode() + content).hexdigest()[:24]
        extension = "png" if mime == "image/png" else "jpeg"
        media_name = f"word/media/connlab-{identity}.{extension}"
        rel_id = f"rIdConnLabPhoto{identity}"
        if media_name in parts and parts[media_name] != content:
            raise ValueError("Photo media identity collision; no output was written.")
        existing = next((item for item in relationships if item.get("Id") == rel_id), None)
        if existing is not None and _relationship_target(existing) != media_name:
            raise ValueError("Photo relationship identity collision; no output was written.")
        if existing is None:
            etree.SubElement(relationships, "{" + NS["pr"] + "}Relationship", Id=rel_id,
                Type=NS["r"] + "/image", Target=media_name.removeprefix("word/"))
        node.set("{" + NS["r"] + "}embed", rel_id)
        additions[media_name] = content
        if not any(item.get("Extension") == extension for item in content_types):
            etree.SubElement(content_types, "{" + NS["ct"] + "}Default", Extension=extension, ContentType=mime)
        changed.append(slot.slot_id)
    if changed:
        parts[DOCUMENT] = etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)
        parts[RELS] = etree.tostring(relationships, xml_declaration=True, encoding="UTF-8", standalone=True)
        if etree.tostring(content_types) != etree.tostring(_xml(parts[TYPES])):
            parts[TYPES] = etree.tostring(content_types, xml_declaration=True, encoding="UTF-8", standalone=True)
        buffer = BytesIO()
        with ZipFile(buffer, "w") as package:
            for item in items:
                package.writestr(item, parts[item.filename])
            for name, content in additions.items():
                if name not in parts:
                    package.writestr(name, content)
        result = buffer.getvalue()
    else:
        result = raw
    if sha256(source.read_bytes()).hexdigest() != expected_source_sha256:
        raise ValueError("Report changed while preparing photos; no output was written.")
    with output.open("xb") as stream:
        stream.write(result)
    return PhotoUpdateResult(bool(changed), sha256(result).hexdigest(), tuple(changed))
