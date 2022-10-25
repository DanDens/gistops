#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))
