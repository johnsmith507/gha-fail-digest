"""Heuristic parser for GitHub Actions logs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .models import FailureDigest, LogSource, StepFailure


TIMESTAMP_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\s+")
GROUP_PREFIX = re.compile(r"^##\[group\](?:Run\s+)?(.+)$")
ERROR_MARKERS = [
    re.compile(r"::error(?:\s+[^:]*)?::(.+)", re.IGNORECASE),
    re.compile(r"##\[error\](.+)", re.IGNORECASE),
    re.compile(r"\berror\b[:\s].+", re.IGNORECASE),
    re.compile(r"\bfailed\b[:\s].+", re.IGNORECASE),
    re.compile(r"Process completed with exit code \d+", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\):"),
    re.compile(r"npm ERR!", re.IGNORECASE),
    re.compile(r"\bTS\d{4}:"),
    re.compile(r"\bESLint\b|\blint\b", re.IGNORECASE),
]


@dataclass(frozen=True)
class _Step:
    source: str
    name: str
    start_line: int
    lines: list[str]


def _clean_line(line: str) -> str:
    line = line.rstrip("\n")
    return TIMESTAMP_PREFIX.sub("", line)


def _split_steps(source: LogSource) -> list[_Step]:
    current_name = source.name
    current_start = 1
    current_lines: list[str] = []
    steps: list[_Step] = []

    for idx, raw in enumerate(source.text.splitlines(), start=1):
        line = _clean_line(raw)
        match = GROUP_PREFIX.match(line)
        if match:
            if current_lines:
                steps.append(_Step(source.name, current_name, current_start, current_lines))
            current_name = match.group(1).strip()
            current_start = idx
            current_lines = [line]
            continue
        current_lines.append(line)

    if current_lines:
        steps.append(_Step(source.name, current_name, current_start, current_lines))
    return steps


def _line_score(line: str) -> int:
    if "Process completed with exit code" in line:
        return 2

    score = 0
    for marker in ERROR_MARKERS:
        if marker.search(line):
            score += 5
    if re.search(r"\bAssertionError\b|\bExpected\b|\breceived\b", line):
        score += 3
    if re.search(r"\bat\s+.+\(.+:\d+:\d+\)", line) or re.search(r'File ".+", line \d+', line):
        score += 2
    return score


def _step_score(step: _Step) -> int:
    score = 0
    for line in step.lines:
        score += _line_score(line)
    if any("Process completed with exit code" in line for line in step.lines):
        score += 4
    return score


def _first_error_index(lines: list[str]) -> int | None:
    best_idx: int | None = None
    best_score = 0
    for idx, line in enumerate(lines):
        score = _line_score(line)
        if score > best_score:
            best_idx = idx
            best_score = score
    return best_idx


def _extract_error_message(lines: list[str], idx: int | None) -> str:
    if idx is None:
        return "No explicit error marker found."
    line = lines[idx].strip()
    annotation = re.match(r"::error(?:\s+[^:]*)?::(.+)", line, re.IGNORECASE)
    if annotation:
        return annotation.group(1).strip()
    issue_command = re.match(r"##\[error\](.+)", line, re.IGNORECASE)
    if issue_command:
        return issue_command.group(1).strip()
    return line


def _extract_context(lines: list[str], idx: int | None, radius: int = 4) -> list[str]:
    if idx is None:
        return []
    start = max(0, idx - radius)
    end = min(len(lines), idx + radius + 1)
    return [line for line in lines[start:end] if line.strip()]


def _extract_stack_trace(lines: list[str], idx: int | None) -> list[str]:
    if idx is None:
        return []

    trace: list[str] = []

    traceback_start = next(
        (i for i, line in enumerate(lines) if "Traceback (most recent call last):" in line),
        None,
    )
    if traceback_start is not None:
        for line in lines[traceback_start:]:
            if not line.strip() and trace:
                break
            trace.append(line)
        return trace[:25]

    for line in lines[max(0, idx - 2): idx + 18]:
        if re.search(r"\bat\s+.+\(.+:\d+:\d+\)", line) or re.search(r'File ".+", line \d+', line):
            trace.append(line)
        elif trace and line.strip().startswith(("at ", "Caused by:", "Error:")):
            trace.append(line)

    return trace[:25]


def _classify(lines: Iterable[str]) -> tuple[str, str]:
    text = "\n".join(lines)
    lower = text.lower()

    if "pytest" in lower or "assertionerror" in lower or re.search(r"=+ FAILURES =+", text):
        return "test_failure", "fix failing tests"
    if "jest" in lower or re.search(r"\bexpect\(.+\)", text) or "snapshot" in lower:
        return "test_failure", "fix failing tests"
    if re.search(r"\bTS\d{4}:", text) or "tsc " in lower or "typescript" in lower:
        return "build_error", "fix compile/type errors"
    if "eslint" in lower or "pylint" in lower or "ruff" in lower or "lint" in lower:
        return "lint_error", "fix lint/style violations"
    if "npm err!" in lower or "pip install" in lower or "could not resolve dependency" in lower:
        return "dependency_error", "fix dependency/install problem"
    if "docker build" in lower or "dockerfile" in lower:
        return "build_error", "fix build/container configuration"
    return "unknown_failure", "inspect failing step"


def _failure_from_step(step: _Step) -> StepFailure | None:
    if _step_score(step) <= 0:
        return None
    idx = _first_error_index(step.lines)
    category, fix_category = _classify(step.lines)
    return StepFailure(
        source=step.source,
        step_name=step.name,
        category=category,
        suggested_fix_category=fix_category,
        error_message=_extract_error_message(step.lines, idx),
        stack_trace=_extract_stack_trace(step.lines, idx),
        context=_extract_context(step.lines, idx),
        line_number=(step.start_line + idx) if idx is not None else None,
    )


def parse_logs(sources: Iterable[LogSource]) -> FailureDigest:
    """Parse one or more CI logs into a structured failure digest."""

    materialized = list(sources)
    failures: list[StepFailure] = []

    for source in materialized:
        for step in _split_steps(source):
            failure = _failure_from_step(step)
            if failure:
                failures.append(failure)

    failures.sort(key=lambda failure: (failure.source, failure.line_number or 10**9))

    if not failures:
        return FailureDigest(
            failing_step_name=None,
            category="no_failure_detected",
            suggested_fix_category="inspect full logs",
            error_message=None,
            stack_trace=[],
            failures=[],
            source_count=len(materialized),
        )

    primary = failures[0]
    return FailureDigest(
        failing_step_name=primary.step_name,
        category=primary.category,
        suggested_fix_category=primary.suggested_fix_category,
        error_message=primary.error_message,
        stack_trace=primary.stack_trace,
        failures=failures,
        source_count=len(materialized),
    )
