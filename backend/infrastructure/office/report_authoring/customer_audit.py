"""Read-only customer-package checks, including content invisible in the Word body.

This is a disclosure check, not an engineering approval or an OCR substitute. Explicit visual
reviews of binary/image parts bind to their exact hashes; unknown contents never silently pass.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import posixpath
import re
from typing import Mapping, Sequence
import unicodedata
from urllib.parse import unquote
from zipfile import BadZipFile, ZipFile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


@dataclass(frozen=True)
class CustomerIssue:
    code: str
    location: str
    message: str
    sha256: str | None = None


@dataclass(frozen=True)
class CustomerAudit:
    passed: bool
    issues: tuple[CustomerIssue, ...]
    package_sha256: str
    checked_parts: int


def _normalized(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", value).casefold().split())


def _owner(relationship_part: str) -> str:
    if relationship_part == "_rels/.rels":
        return ""
    parent, leaf = relationship_part.rsplit("/_rels/", 1)
    return parent + "/" + leaf.removesuffix(".rels")


def audit_customer_package(path: Path, *, sensitive_terms: Sequence[str] = (),
                           forbidden_project_ids: Sequence[str] = (),
                           reviewed_parts: Mapping[str, str] | None = None) -> CustomerAudit:
    """Check saved bytes. reviewed_parts comes from retained explicit user review decisions."""
    path = Path(path)
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if len(raw) > 60 * 1024 * 1024:
        return CustomerAudit(False, (CustomerIssue("package_limit", "package", "Report exceeds the inspection size limit."),), digest, 0)
    try:
        with ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > 4000 or sum(entry.file_size for entry in entries) > 200 * 1024 * 1024:
                raise ValueError("Package inspection limit exceeded.")
            if len({entry.filename for entry in entries}) != len(entries):
                raise ValueError("Duplicate package entries.")
            parts = {entry.filename: archive.read(entry) for entry in entries}
    except (BadZipFile, ValueError, RuntimeError) as exc:
        return CustomerAudit(False, (CustomerIssue("unreadable_package", "package", str(exc)),), digest, 0)
    issues: list[CustomerIssue] = []
    trees = {}
    terms = tuple(_normalized(term) for term in sensitive_terms if term.strip())
    old_ids = tuple(_normalized(term) for term in forbidden_project_ids if term.strip())
    reviews = reviewed_parts or {}
    if "word/document.xml" not in parts:
        issues.append(CustomerIssue("missing_document", "package", "A readable Word document is required."))
    for name, content in parts.items():
        if not name.endswith((".xml", ".rels")):
            continue
        try:
            tree = etree.fromstring(content, parser=etree.XMLParser(resolve_entities=False, no_network=True))
            if tree.getroottree().docinfo.doctype:
                raise ValueError("Document type declarations are unsupported.")
        except (etree.XMLSyntaxError, ValueError):
            issues.append(CustomerIssue("unreadable_part", name, "This XML part could not be checked safely."))
            continue
        trees[name] = tree
        texts = list(tree.itertext())
        # Run-split grades and text hidden in field instructions/properties are included.
        values = [*texts, *(value for node in tree.iter() for value in node.attrib.values())]
        normalized = _normalized(unquote(" ".join(values)))
        if any(term in normalized for term in terms):
            issues.append(CustomerIssue("sensitive_text", name, "A restricted material or disclosure term remains."))
        if any(term in normalized for term in old_ids):
            issues.append(CustomerIssue("old_project_identity", name, "A previous project's identity remains."))
        if any(node.tag in {f"{{{W}}}{tag}" for tag in ("ins", "del", "moveFrom", "moveTo")} for node in tree.iter()):
            issues.append(CustomerIssue("tracked_changes", name, "Tracked changes need review before delivery."))
        if any(node.tag == f"{{{W}}}comment" for node in tree.iter()):
            issues.append(CustomerIssue("comments", name, "Reviewer comments remain in the customer package."))
        if any(node.tag in {f"{{{W}}}vanish", f"{{{W}}}webHidden"} and node.get(f"{{{W}}}val", "1") not in {"0", "false", "off"} for node in tree.iter()):
            issues.append(CustomerIssue("hidden_text", name, "Hidden text needs review before delivery."))
        instructions = " ".join(
            (node.text or "") if node.tag == f"{{{W}}}instrText" else node.get(f"{{{W}}}instr", "")
            for node in tree.iter() if node.tag in {f"{{{W}}}instrText", f"{{{W}}}fldSimple"}
        )
        if re.search(r"\b(?:DDEAUTO|DDE|INCLUDETEXT|INCLUDEPICTURE|LINK)\b", instructions, re.IGNORECASE):
            issues.append(CustomerIssue("external_field", name, "A field can load external content; inspect it before delivery."))

    used_media: set[str] = set()
    for name, tree in trees.items():
        if not name.endswith(".rels"):
            continue
        try:
            owner = _owner(name)
        except ValueError:
            issues.append(CustomerIssue("unknown_relationship_part", name, "Unrecognized relationship location."))
            continue
        owner_tree = trees.get(owner)
        used_ids = set()
        if owner_tree is not None:
            used_ids = {value for node in owner_tree.iter() for key, value in node.attrib.items() if key.startswith("{" + R + "}")}
        for relation in tree:
            target = unquote(relation.get("Target", ""))
            if relation.get("TargetMode") == "External":
                issues.append(CustomerIssue("external_relationship", name, "An external link or linked object remains."))
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(owner), target))
            if target.startswith("/"):
                target = target.lstrip("/")
            if target.startswith("word/media/") and relation.get("Id") in used_ids:
                used_media.add(target)

    for name, content in parts.items():
        checksum = sha256(content).hexdigest()
        if any(token in name.casefold() for token in ("vbaproject", "/activex/")):
            issues.append(CustomerIssue("active_content", name, "Executable Office content is not allowed in a customer copy.", checksum))
        elif name.startswith("word/media/"):
            if name not in used_media:
                issues.append(CustomerIssue("unreferenced_media", name,
                    "An unused image remains in the package and may contain previous-project content.", checksum))
            elif reviews.get(name) != checksum:
                issues.append(CustomerIssue("visual_review_required", name,
                    "Check visible image text/content; automated XML checks cannot inspect its pixels.", checksum))
        elif name.startswith("word/embeddings/") and reviews.get(name) != checksum:
            issues.append(CustomerIssue("unreviewed_embedding", name,
                "An embedded object cannot be certified by the text check; review this exact object.", checksum))
        elif not name.endswith((".xml", ".rels", "/")) and reviews.get(name) != checksum:
            # Thumbnails, altChunk HTML/RTF, fonts and other opaque parts can carry
            # information outside the visible document. Never silently skip them.
            issues.append(CustomerIssue("unreviewed_package_part", name,
                "This package part is outside the XML text check; review its exact contents before delivery.", checksum))
    # Never mark a concurrently changed package as reviewed.
    if sha256(path.read_bytes()).hexdigest() != digest:
        issues.append(CustomerIssue("package_changed", "package", "Report changed during inspection; run the check again."))
    return CustomerAudit(not issues, tuple(issues), digest, len(parts))
