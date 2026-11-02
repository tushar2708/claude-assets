#!/usr/bin/env python3
"""Run the canonical GEO PDF report generator from this skill entry point."""

from pathlib import Path
import runpy


CANONICAL_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "react-seo-planner"
    / "scripts"
    / "generate_pdf_report.py"
)
runpy.run_path(str(CANONICAL_SCRIPT), run_name="__main__")
