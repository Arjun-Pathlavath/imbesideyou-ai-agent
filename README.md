
# Assignment Quality Audit Agent

A Python-based, read-only audit agent that inspects an existing assignment project, identifies potential quality and evaluation risks, and provides recommendations without modifying the original assignment files.

## Features

- Workspace file listing with exclusions for virtual environments and cache directories.
- Safe file reading with path-traversal protection and file-size limits.
- Inspection of assignment source code, tests, and reports.
- Audit findings for evaluation coverage, human oversight, business-impact measurement, and date validation.
- ISO date validation utility with calendar-aware checks.
- Automated regression tests using pytest.

## Project Structure

```text
imbesideyou-ai-agent/
|-- agent/
|   |-- __init__.py
|   `-- core.py
|-- tests/
|   |-- test_assignment_quality.py
|   `-- test_workspace.py
|-- tools/
|   |-- assignment_inspector.py
|   `-- workspace.py
|-- main.py
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Requirements

- Python 3.12 or compatible
- pytest 9.1.1

## Setup on Windows

### 1. Create a virtual environment

```cmd
python -m venv .venv
```

### 2. Activate the environment

```cmd
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

## Run the Tests

Run the complete test suite:

```cmd
python -m pytest -v
```

The latest local test run passed 23 tests, with 8 additional subtests passing.

## Run the Assignment Audit

```cmd
python -m agent.core
```

The audit reports findings with priorities, supporting evidence, and recommendations. It also runs self-checks for the agent's date-validation utility.

## Configuration

The assignment inspector currently uses a local Windows path configured in `tools/assignment_inspector.py`.

Update `ASSIGNMENT_ROOT` in that file before using the agent on another machine. Only inspect assignment files you are authorized to access.

## Safety and Limitations

- This is a rule-based audit prototype, not an autonomous decision-making system.
- Some findings rely on text matching and do not independently prove runtime behavior.
- The agent reads selected assignment files and does not intentionally modify them.
- The original assignment's date-validation limitation remains unfixed; the agent reports the issue rather than changing the original project.
- Classification accuracy and business impact require separate empirical evaluation.
- Human review should remain required for consequential workflow decisions.

## Future Improvements

- Replace hard-coded paths with configurable settings.
- Strengthen source checks beyond text matching.
- Add structured JSON audit output.
- Expand tests for malformed, contradictory, and incomplete inputs.
- Add reproducible evaluation reports.
