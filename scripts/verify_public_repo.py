"""Verify the public repository package before publication."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
    "docs/github-actions-ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "assets/demo.svg",
    "docs/agent-handoff.md",
    "docs/examples.md",
    "docs/failure-patterns.md",
    "examples/demo-transcript.md",
    "src/gha_fail_digest/cli.py",
    "src/gha_fail_digest/parser.py",
    "tests/test_cli.py",
    "tests/test_parser.py",
}

README_TERMS = [
    "GitHub Actions",
    "coding agents",
    "local",
    "no telemetry",
    "GITHUB_TOKEN",
    "failure patterns",
]

FORBIDDEN_PATH_PARTS = {
    "sales",
    "dist",
    "content",
    "metrics",
    "__pycache__",
}


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def verify_required_files() -> None:
    missing = [path for path in sorted(REQUIRED_FILES) if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")


def verify_no_private_sales_artifacts() -> None:
    bad_paths: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in FORBIDDEN_PATH_PARTS for part in rel_parts):
            bad_paths.append(str(path.relative_to(ROOT)))
        if path.suffix == ".pyc":
            bad_paths.append(str(path.relative_to(ROOT)))
    if bad_paths:
        raise SystemExit(f"Public repo contains forbidden generated/private paths: {bad_paths}")


def cleanup_generated_python() -> None:
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    child.unlink()
            path.rmdir()
    for path in ROOT.rglob("*.pyc"):
        path.unlink()


def verify_readme_positioning() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    missing = [term for term in README_TERMS if term.lower() not in text]
    if missing:
        raise SystemExit(f"README missing positioning terms: {missing}")


def verify_tests() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])


def verify_compile() -> None:
    run([sys.executable, "-m", "compileall", "src", "tests"])


def verify_cli() -> None:
    result = run(
        [
            sys.executable,
            "-m",
            "gha_fail_digest.cli",
            "tests/fixtures/typescript.log",
        ]
    )
    payload = json.loads(result.stdout)
    assert payload["category"] == "build_error"
    assert payload["failing_step_name"] == "npm run build"


def main() -> int:
    cleanup_generated_python()
    verify_required_files()
    verify_no_private_sales_artifacts()
    verify_readme_positioning()
    verify_tests()
    verify_compile()
    verify_cli()
    cleanup_generated_python()
    verify_no_private_sales_artifacts()
    print("public repo verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
