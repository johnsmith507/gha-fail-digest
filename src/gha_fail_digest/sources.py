"""Input loading for local files, ZIP archives, stdin, and GitHub run URLs."""

from __future__ import annotations

import io
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from .models import LogSource


RUN_URL = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/actions/runs/(\d+)(?:/.*)?$")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _sources_from_zip(path: Path) -> list[LogSource]:
    with zipfile.ZipFile(path) as archive:
        sources: list[LogSource] = []
        for name in sorted(archive.namelist()):
            if name.endswith("/") or name.startswith("__MACOSX/"):
                continue
            data = archive.read(name)
            sources.append(LogSource(name=name, text=data.decode("utf-8", errors="replace")))
        return sources


def _sources_from_directory(path: Path) -> list[LogSource]:
    sources: list[LogSource] = []
    for child in sorted(path.rglob("*")):
        if child.is_file() and child.suffix.lower() in {".log", ".txt"}:
            sources.append(LogSource(name=str(child.relative_to(path)), text=_read_text(child)))
    return sources


def _github_logs_url(run_url: str) -> tuple[str, str]:
    match = RUN_URL.match(run_url)
    if not match:
        raise ValueError("Expected GitHub Actions run URL like https://github.com/owner/repo/actions/runs/123")
    owner, repo, run_id = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    return f"{owner}/{repo}#{run_id}", api_url


def _download_github_logs(run_url: str) -> list[LogSource]:
    label, api_url = _github_logs_url(run_url)
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gha-fail-digest/0.1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 404}:
            raise RuntimeError(
                "Could not download GitHub Actions logs. Set GITHUB_TOKEN for private repos "
                "or runs that require authentication."
            ) from exc
        raise

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        sources: list[LogSource] = []
        for name in sorted(archive.namelist()):
            if name.endswith("/"):
                continue
            data = archive.read(name)
            sources.append(LogSource(name=f"{label}/{name}", text=data.decode("utf-8", errors="replace")))
        return sources


def load_sources(inputs: list[str]) -> list[LogSource]:
    """Load all CLI inputs as log sources."""

    if not inputs or inputs == ["-"]:
        return [LogSource(name="stdin", text=sys.stdin.read())]

    sources: list[LogSource] = []
    for value in inputs:
        if RUN_URL.match(value):
            sources.extend(_download_github_logs(value))
            continue

        path = Path(value)
        if path.is_dir():
            sources.extend(_sources_from_directory(path))
        elif path.suffix.lower() == ".zip":
            sources.extend(_sources_from_zip(path))
        elif path.exists():
            sources.append(LogSource(name=str(path), text=_read_text(path)))
        else:
            raise FileNotFoundError(f"Input not found: {value}")

    if not sources:
        raise ValueError("No log files found in input.")
    return sources
