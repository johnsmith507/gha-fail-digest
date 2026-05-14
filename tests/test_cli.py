import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gha_fail_digest.cli", *args],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_cli_outputs_json(self) -> None:
        result = run_cli(str(FIXTURES / "typescript.log"))

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["category"], "build_error")
        self.assertEqual(payload["failing_step_name"], "npm run build")

    def test_cli_outputs_text(self) -> None:
        result = run_cli("--format", "text", str(FIXTURES / "pytest.log"))

        self.assertEqual(result.returncode, 0)
        self.assertIn("Failing step: pytest", result.stdout)
        self.assertIn("fix failing tests", result.stdout)

    def test_cli_outputs_markdown(self) -> None:
        result = run_cli("--format", "markdown", str(FIXTURES / "jest.log"))

        self.assertEqual(result.returncode, 0)
        self.assertIn("### GitHub Actions Failure Summary", result.stdout)
        self.assertIn("**Failing step:** `npm test`", result.stdout)
        self.assertIn("#### Stack Trace", result.stdout)

    def test_cli_reports_missing_input(self) -> None:
        result = run_cli("does-not-exist.log")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Input not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
