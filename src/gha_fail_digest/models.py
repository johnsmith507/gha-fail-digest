"""Data models for parsed CI failures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LogSource:
    """One log stream or file."""

    name: str
    text: str


@dataclass(frozen=True)
class StepFailure:
    """The highest-signal failure extracted from one CI step."""

    source: str
    step_name: str
    category: str
    suggested_fix_category: str
    error_message: str
    stack_trace: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    line_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FailureDigest:
    """Structured summary of a GitHub Actions failure."""

    failing_step_name: str | None
    category: str
    suggested_fix_category: str
    error_message: str | None
    stack_trace: list[str]
    failures: list[StepFailure]
    source_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
