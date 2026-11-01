"""Turns the pytest JUnit XML file into test-report.json.

Usage: python ci/build_report.py results.xml test-report.json
Repository, branch, commit and run id are read from the GitHub Actions
environment variables (GITHUB_REPOSITORY, GITHUB_REF_NAME, GITHUB_SHA, ...).
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def read_tests(xml_path):
    tests = []
    if not os.path.exists(xml_path):
        # pytest crashed before writing results (e.g. import error)
        return [{
            "name": "pytest_run",
            "result": "failed",
            "failure_message": "No test results file was produced. The test run crashed.",
        }]

    root = ET.parse(xml_path).getroot()
    for case in root.iter("testcase"):
        name = case.get("name")
        result, message = "passed", None
        for tag in ("failure", "error"):
            node = case.find(tag)
            if node is not None:
                result = "failed"
                message = (node.get("message") or node.text or "").strip()
        if case.find("skipped") is not None:
            result = "skipped"
        tests.append({"name": name, "result": result, "failure_message": message})
    return tests


def build_report(xml_path):
    tests = read_tests(xml_path)
    passed = sum(1 for t in tests if t["result"] == "passed")
    failed = sum(1 for t in tests if t["result"] == "failed")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "local/assignment-portal")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")

    return {
        "repository": repo,
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": run_id,
        "pipeline_run_number": os.environ.get("GITHUB_RUN_NUMBER", "0"),
        "pipeline_run_url": f"{server}/{repo}/actions/runs/{run_id}",
        "triggered_by": os.environ.get("GITHUB_ACTOR", "local"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tests": tests,
        "summary": {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "overall_status": "PASSED" if failed == 0 and tests else "FAILED",
        },
    }


if __name__ == "__main__":
    xml_file = sys.argv[1] if len(sys.argv) > 1 else "results.xml"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "test-report.json"
    report = build_report(xml_file)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report["summary"], indent=2))
