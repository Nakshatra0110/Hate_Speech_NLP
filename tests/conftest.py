import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Prevent Intel OpenMP duplicate runtime conflicts on Windows
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
