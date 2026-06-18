import os
import sys

# Ensure `import app` works when running `pytest livetests/` from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
