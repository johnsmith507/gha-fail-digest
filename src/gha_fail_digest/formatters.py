"""Output formatting helpers."""

from __future__ import annotations

import json

from .models import FailureDigest


def to_json(digest: FailureDigest, pretty: bool = True) -> str:
    return json.dumps(digest.to_dict(), indent=2 if pretty else None, sort_keys=True)


def to_text(digest: FailureDigest) -> str:
    if not digest.failures:
        return "No failure detected. Inspect the full logs if the workflow still failed."

    lines = [
        f"Failing step: {digest.failing_step_name}",
        f"Category: {digest.category}",
        f"Suggested fix category: {digest.suggested_fix_category}",
        f"Error: {digest.error_message}",
    ]

    if digest.stack_trace:
        lines.append("")
        lines.append("Stack trace:")
        lines.extend(f"  {line}" for line in digest.stack_trace[:12])

    if len(digest.failures) > 1:
        lines.append("")
        lines.append(f"Other detected failures: {len(digest.failures) - 1}")
        for failure in digest.failures[1:6]:
            lines.append(f"  - {failure.step_name}: {failure.error_message}")

    return "\n".join(lines)


def to_markdown(digest: FailureDigest) -> str:
    if not digest.failures:
        return "### GitHub Actions Failure Summary\n\nNo failure detected. Inspect the full logs if the workflow still failed."

    lines = [
        "### GitHub Actions Failure Summary",
        "",
        f"- **Failing step:** `{digest.failing_step_name}`",
        f"- **Category:** `{digest.category}`",
        f"- **Suggested fix:** {digest.suggested_fix_category}",
        f"- **Primary error:** `{digest.error_message}`",
    ]

    if digest.stack_trace:
        lines.extend(["", "#### Stack Trace", "", "```text"])
        lines.extend(digest.stack_trace[:12])
        lines.append("```")

    primary_context = digest.failures[0].context if digest.failures else []
    if primary_context:
        lines.extend(["", "#### Nearby Context", "", "```text"])
        lines.extend(primary_context[:12])
        lines.append("```")

    if len(digest.failures) > 1:
        lines.extend(["", "#### Other Detected Failures"])
        for failure in digest.failures[1:6]:
            lines.append(f"- `{failure.step_name}`: `{failure.error_message}`")

    return "\n".join(lines)
