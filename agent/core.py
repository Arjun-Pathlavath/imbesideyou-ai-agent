
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

    if "not independently verified classification accuracy" in report:
        add_finding(
            "HIGH",
            "Classification accuracy remains unverified",
            "The report distinguishes workflow coverage from independently "
            "verified classification accuracy.",
            "Create a manually labelled evaluation set and report "
            "per-category precision, recall, and confusion cases.",
        )

    if "Only **three sessions**" in report:
        add_finding(
            "HIGH",
            "Ground-truth coverage is limited",
            "The report says only three sessions overlap the available "
            "ground-truth and raw-event coverage.",
            "Evaluate additional complete sessions before claiming "
            "generalizable boundary-detection performance.",
        )

    if (
        "automatic_approval" in implementation
        and re.search(r'"automatic_approval"\s*:\s*False', implementation)
    ):
        add_finding(
            "HIGH",
            "Human control is preserved",
            "The implementation explicitly returns automatic_approval=False.",
            "Retain this safeguard and test it across all workflows and "
            "error paths.",
        )

    if "test_human_confirmation_always_required" in tests:
        add_finding(
            "MEDIUM",
            "Safety regression tests exist",
            "The existing tests include a human-confirmation safeguard check.",
            "Extend coverage to malformed, contradictory, and incomplete "
            "inputs across all eight workflow families.",
        )

    if "No defensible time-saving percentage" in report:
        add_finding(
            "HIGH",
            "Business impact has not been measured",
            "The report says baseline handling time and reviewer correction "
            "time have not been measured.",
            "Run a controlled manual-versus-assisted evaluation measuring "
            "handling time, corrections, and exception rates.",
        )

    # Inspect the real source for calendar-aware date validation.
    has_date_extraction = (
        "due_or_effective_date" in implementation
        or "date" in implementation.lower()
    )
    has_calendar_validation = (
        "date.fromisoformat" in implementation
        or "datetime.strptime" in implementation
        or "datetime.fromisoformat" in implementation
    )

    if has_date_extraction and not has_calendar_validation:
        add_finding(
            "HIGH",
            "Extracted dates lack calendar-aware validation",
            "The source extracts date fields but no calendar-aware date "
            "parser was found in the implementation.",
            "Validate extracted dates with calendar-aware parsing and flag "
            "impossible dates for human review.",
        )

    # Demonstrate that the agent's date validator handles edge cases.
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
