"""Configure isolated paths before application modules are imported by pytest."""
import os
import tempfile
from pathlib import Path

_TEST_ROOT = Path(tempfile.gettempdir()) / f"arteryvision-tests-{os.getpid()}"
_TEST_ROOT.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_ROOT / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(_TEST_ROOT / "uploads")
os.environ["REPORT_DIR"] = str(_TEST_ROOT / "reports")
os.environ["SECRET_KEY"] = "test-only-secret-key-that-is-long-enough-for-tests"
