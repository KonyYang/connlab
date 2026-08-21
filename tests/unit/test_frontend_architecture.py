from pathlib import Path


FRONTEND_SOURCE = Path(__file__).parents[2] / "frontend" / "src"


def test_frontend_routes_http_through_the_api_boundary() -> None:
    """Feature and page code must not bypass the shared API client."""
    violations = []
    for path in sorted(FRONTEND_SOURCE.rglob("*.ts*")):
        if path.name.endswith((".test.ts", ".test.tsx")) or "api" in path.parts:
            continue
        if "fetch(" in path.read_text(encoding="utf-8"):
            violations.append(path.relative_to(FRONTEND_SOURCE).as_posix())

    assert violations == []
