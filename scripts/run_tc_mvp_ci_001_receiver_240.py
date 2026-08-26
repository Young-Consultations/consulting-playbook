#!/usr/bin/env python3
"""Run target conformance while binding receiver-live evidence to the reviewed 2.4.0 candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_tc_mvp_ci_001 import ROOT, run

EXPECTED_GENERATOR_STATE = "pending-ai-sdlc-v2.3.1-tag"
EXPECTED_RECEIVER_STATE = "pending-ai-sdlc-v2.4.0-tag"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / ".ai-sdlc/conformance/tc-mvp-ci-001.json",
    )
    args = parser.parse_args()
    failures = run(args.report)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    observed = report.get("receiver_live_verification")
    if observed != EXPECTED_GENERATOR_STATE:
        raise SystemExit(
            "unexpected base receiver verification state: "
            f"expected {EXPECTED_GENERATOR_STATE!r}, got {observed!r}"
        )
    report["receiver_live_verification"] = EXPECTED_RECEIVER_STATE
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit("TC-MVP-CI-001 failed:\n- " + "\n- ".join(failures))
    print("TC-MVP-CI-001: target adapter passed; receiver 2.4.0 remains pending publication")


if __name__ == "__main__":
    main()
