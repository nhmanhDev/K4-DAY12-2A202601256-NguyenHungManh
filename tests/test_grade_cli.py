"""Regression tests for the cross-platform grade CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_grade_cli_runs_with_a_cp1252_console():
    """Vietnamese output must not crash on the default legacy Windows console."""
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "cp1252"

    result = subprocess.run(
        [sys.executable, "grade.py", "--no-bonus"],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr.decode("cp1252", errors="replace")
