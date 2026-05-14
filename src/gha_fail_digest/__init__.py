"""GitHub Actions failure digest toolkit."""

from .models import FailureDigest, LogSource, StepFailure
from .parser import parse_logs

__all__ = ["FailureDigest", "LogSource", "StepFailure", "parse_logs"]

__version__ = "0.1.0"
