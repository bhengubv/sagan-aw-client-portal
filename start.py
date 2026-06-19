"""Production entrypoint (Railway / Render / any host that runs `python start.py`).

In DEMO_MODE it seeds the demo data first (so the hosted site shows the sample client and
connected providers), then launches gunicorn. Real production sets DEMO_MODE off and manages
its own data and migrations (see docs/DEPLOYMENT.md).
"""
import os
import sys
import subprocess

if os.environ.get("DEMO_MODE") == "1":
    print("DEMO_MODE: seeding demo data ...", flush=True)
    subprocess.run([sys.executable, "seed.py"], check=False)

port = os.environ.get("PORT", "8000")
# Two workers + threads so the portal can call the mounted sandbox on its own port.
os.execvp("gunicorn", [
    "gunicorn", "app:create_app()",
    "--bind", f"0.0.0.0:{port}",
    "--workers", "2",
    "--threads", "4",
    "--timeout", "60",
    "--access-logfile", "-",
])
