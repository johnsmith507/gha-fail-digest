from pathlib import Path
import unittest

from gha_fail_digest.models import LogSource
from gha_fail_digest.parser import parse_logs


FIXTURES = Path(__file__).parent / "fixtures"


def source(name: str) -> LogSource:
    return LogSource(name=name, text=(FIXTURES / name).read_text(encoding="utf-8"))


class ParserTests(unittest.TestCase):
    def test_detects_pytest_failure(self) -> None:
        digest = parse_logs([source("pytest.log")])

        self.assertEqual(digest.failing_step_name, "pytest")
        self.assertEqual(digest.category, "test_failure")
        self.assertEqual(digest.suggested_fix_category, "fix failing tests")
        self.assertIn("AssertionError", digest.error_message or "")
        self.assertIsNotNone(digest.failures[0].line_number)

    def test_detects_typescript_build_error(self) -> None:
        digest = parse_logs([source("typescript.log")])

        self.assertEqual(digest.failing_step_name, "npm run build")
        self.assertEqual(digest.category, "build_error")
        self.assertIn("TS2322", digest.error_message or "")

    def test_detects_jest_failure_and_stack(self) -> None:
        digest = parse_logs([source("jest.log")])

        self.assertEqual(digest.category, "test_failure")
        self.assertTrue(digest.stack_trace)
        self.assertIn("src/cart.test.ts", "\n".join(digest.stack_trace))

    def test_detects_lint_failure(self) -> None:
        digest = parse_logs([source("lint.log")])

        self.assertEqual(digest.category, "lint_error")
        self.assertEqual(digest.suggested_fix_category, "fix lint/style violations")

    def test_extracts_github_annotation_error_message(self) -> None:
        digest = parse_logs([source("annotation.log")])

        self.assertEqual(digest.failing_step_name, "unit tests")
        self.assertEqual(digest.category, "test_failure")
        self.assertEqual(
            digest.error_message,
            "AssertionError: expected captured amount to equal invoice total",
        )

    def test_reports_no_failure_for_clean_log(self) -> None:
        digest = parse_logs([LogSource(name="clean.log", text="##[group]Run tests\nall good\n")])

        self.assertEqual(digest.category, "no_failure_detected")
        self.assertEqual(digest.failures, [])


if __name__ == "__main__":
    unittest.main()
