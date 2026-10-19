
import ast
import re

from tools.workspace import list_workspace_files, read_workspace_file
from tools.assignment_inspector import (
    list_assignment_files,
    read_assignment_file,
    is_valid_iso_date,
)


def inspect_workspace():
    files = list_workspace_files()
    return {"workspace_files": files, "file_count": len(files)}


def inspect_file(relative_path: str):
    content = read_workspace_file(relative_path)
    return {
        "path": relative_path,
        "characters": len(content),
        "content": content,
    }


def _source_has_false_assignment(source: str, variable_name: str) -> bool:
    """Check Python syntax for a dictionary entry explicitly set to False."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue

        for key, value in zip(node.keys, node.values):
            if (
                isinstance(key, ast.Constant)
                and key.value == variable_name
                and isinstance(value, ast.Constant)
                and value.value is False
            ):
                return True

    return False


def _has_calendar_validation(source: str) -> bool:
    """Look for common calendar-aware date parsing calls in Python source."""
    patterns = (
        r"\bdate\s*\.\s*fromisoformat\s*\(",
        r"\bdatetime\s*\.\s*fromisoformat\s*\(",
        r"\bdatetime\s*\.\s*strptime\s*\(",
        r"\bstrptime\s*\(",
    )
    return any(re.search(pattern, source) for pattern in patterns)


def build_assignment_audit():
    """Create source-based findings without modifying assignment files."""
    report = read_assignment_file("reports/final_report.md")
    implementation = read_assignment_file("src/expense_review.py")
    tests = read_assignment_file("tests/test_expense_review.py")

    findings = []

    def add_finding(priority, title, evidence, recommendation):
        findings.append({
            "priority": priority,
            "title": title,
            "evidence": evidence,
            "recommendation": recommendation,
        })

    report_lower = report.lower()

    if (
        "classification accuracy" in report_lower
        and any(
            phrase in report_lower
            for phrase in (
                "not independently verified",
                "not verified",
                "has not been verified",
                "unverified",
            )
        )
    ):
        add_finding(
            "HIGH",
            "Classification accuracy remains unverified",
            "The report discusses classification accuracy but also indicates "
            "that it has not been independently verified.",
            "Create a manually labelled evaluation set and report "
            "per-category precision, recall, and confusion cases.",
        )

    limited_ground_truth = (
        re.search(r"\bthree sessions\b", report_lower)
        or re.search(r"\b3 sessions\b", report_lower)
    )
    mentions_overlap = (
        "ground-truth" in report_lower
        or "ground truth" in report_lower
    )

    if limited_ground_truth and mentions_overlap:
        add_finding(
            "HIGH",
            "Ground-truth coverage may be limited",
            "The report mentions three sessions in its ground-truth "
            "discussion. Confirm the overlap count and coverage before "
            "generalizing performance.",
            "Evaluate additional complete sessions and clearly state "
            "the sample size and limitations.",
        )

    if _source_has_false_assignment(implementation, "automatic_approval"):
        add_finding(
            "HIGH",
            "Human control is preserved in the inspected implementation",
            "A Python dictionary explicitly sets automatic_approval to False.",
            "Retain this safeguard and test it across workflows and "
            "error paths. This source check alone does not prove every "
            "execution path is safe.",
        )

    if re.search(
        r"\btest_human_confirmation_always_required\b",
        tests,
    ):
        add_finding(
            "MEDIUM",
            "Human-confirmation regression test is present",
            "The test source contains a test named "
            "test_human_confirmation_always_required.",
            "Extend coverage to malformed, contradictory, and incomplete "
            "inputs across all workflow families.",
        )

    if (
        "time-saving percentage" in report_lower
        or "handling time" in report_lower
        or "business impact" in report_lower
    ) and any(
        phrase in report_lower
        for phrase in (
            "not measured",
            "no defensible",
            "has not been measured",
            "not yet measured",
        )
    ):
        add_finding(
            "HIGH",
            "Business impact needs measured evidence",
            "The report discusses handling time, time savings, or business "
            "impact alongside a statement that the evidence is not measured.",
            "Run a controlled manual-versus-assisted evaluation measuring "
            "handling time, reviewer corrections, and exception rates.",
        )

    has_date_extraction = (
        "due_or_effective_date" in implementation
        or re.search(r"\bdate\b", implementation.lower()) is not None
    )

    if has_date_extraction and not _has_calendar_validation(implementation):
        add_finding(
            "HIGH",
            "Extracted dates lack calendar-aware validation",
            "The inspected implementation references date-related fields "
            "but contains no recognized calendar-aware parsing call.",
            "Validate extracted dates with calendar-aware parsing and flag "
            "impossible dates for human review. Review the code manually "
            "because this check recognizes common patterns, not every "
            "possible validation implementation.",
        )

    date_checks = {
        "valid_date": is_valid_iso_date("2026-07-14"),
        "impossible_month_day": is_valid_iso_date("2026-99-99"),
        "nonexistent_calendar_date": is_valid_iso_date("2026-02-30"),
        "malformed_date": is_valid_iso_date("not-a-date"),
    }

    return {
        "assignment_file_count": len(list_assignment_files()),
        "findings": findings,
        "date_validator_checks": date_checks,
        "source_files_inspected": [
            "reports/final_report.md",
            "src/expense_review.py",
            "tests/test_expense_review.py",
        ],
    }


def run_agent():
    audit = build_assignment_audit()

    print("=== Assignment Quality Audit ===")
    print(f"Files available: {audit['assignment_file_count']}")
    print(f"Findings: {len(audit['findings'])}")

    for index, finding in enumerate(audit["findings"], start=1):
        print(f"\n{index}. [{finding['priority']}] {finding['title']}")
        print(f"Evidence: {finding['evidence']}")
        print(f"Recommendation: {finding['recommendation']}")

    print("\n=== Date Validator Self-Checks ===")
    for check, result in audit["date_validator_checks"].items():
        print(f"{check}: {result}")

    print("\nAudit complete. Original assignment files were only read.")


if __name__ == "__main__":
    run_agent()
