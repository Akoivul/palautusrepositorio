import sys
from pathlib import Path

# Ensure project root is on sys.path so that 'src' package is importable
ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

for path in (ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
