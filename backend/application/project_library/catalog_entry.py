"""Resolve catalog navigation aliases without using display numbers as identity."""
def catalog_entry(catalog, key):
    rows = catalog.catalog()
    entry = next((row for row in rows if row["key"] == key), None)
    if entry is None and key.startswith("member:"):
        entry = next((row for row in rows if row.get("member_id") == key.removeprefix("member:")), None)
    if entry is None:
        raise LookupError("Material entry not found. Refresh the library.")
    return entry
