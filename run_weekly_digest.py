from pathlib import Path
import subprocess
import sys

project_folder = Path(__file__).resolve().parent

# Generate the report first.
subprocess.run(
    [sys.executable, str(project_folder / "weekly_digest.py")],
    cwd=project_folder,
    check=True,
)

# Send only if report generation succeeded.
subprocess.run(
    [
        sys.executable,
        str(project_folder / "send_digest.py"),
        "--send",
    ],
    cwd=project_folder,
    check=True,
)