"""Run the provider sandbox:  python run_sandbox.py  (http://127.0.0.1:5050).

In dev, configure the portal's provider base_urls to http://127.0.0.1:5050/<provider>
(seed.py does this for the demo tenant) so 'Refresh from providers' really fetches.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sandbox import create_sandbox_app

app = create_sandbox_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
