"""Local entrypoint:  python run.py  (http://127.0.0.1:5000)."""
import os
import sys

# Make the app importable no matter what the launcher's working directory is.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
