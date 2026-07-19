"""Curated deterministic method template fallback library for Matrix rows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MethodTemplateEntry:
    """One curated template family for row-level MCR fallback."""

    family: str
    aliases: tuple[str, ...]
    fallback_method: str | None = None
    fallback_condition: str | None = None
    fallback_requirement: str | None = None
    provenance: str = "connlab-template-library"


METHOD_TEMPLATE_LIBRARY: tuple[MethodTemplateEntry, ...] = (
    MethodTemplateEntry(
        family="visual",
        aliases=(
            "visual examination",
            "visual inspection",
            "examination",
            "examination of product",
            "visual check",
        ),
        fallback_method="EIA-364-18B",
        fallback_condition="10x min magnification",
        fallback_requirement="No detrimental condition",
        provenance="lab-default-visual-revision",
    ),
    MethodTemplateEntry(
        family="llcr",
        aliases=(
            "llcr",
            "low level contact resistance",
            "low-level contact resistance",
            "contact resistance (low level)",
        ),
        fallback_method="EIA-364-23",
        provenance="approved-family-fallback",
    ),
    MethodTemplateEntry(
        family="mfg",
        aliases=("mfg", "mixed flowing gas", "mixed-flowing gas"),
        fallback_method="EIA-364-65",
        provenance="approved-family-fallback",
    ),
    MethodTemplateEntry(
        family="thermal_shock",
        aliases=("thermal shock",),
        fallback_requirement="No damage",
        provenance="approved-empty-requirement-fallback",
    ),
    MethodTemplateEntry(
        family="temperature_life",
        aliases=("temperature life",),
        fallback_requirement="No damage",
        provenance="approved-empty-requirement-fallback",
    ),
    MethodTemplateEntry(
        family="durability",
        aliases=("durability", "mechanical operation", "mating durability", "unmating durability"),
        fallback_method="EIA-364-09",
        provenance="approved-family-fallback",
    ),
    MethodTemplateEntry(
        family="vibration",
        aliases=("vibration", "random vibration", "sinusoidal vibration"),
        fallback_method="EIA-364-28",
        provenance="approved-family-fallback",
    ),
    MethodTemplateEntry(
        family="shock",
        aliases=("mechanical shock", "shock"),
        fallback_method="EIA-364-27",
        provenance="approved-family-fallback",
    ),
)
