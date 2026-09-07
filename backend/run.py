import os
import sys
import subprocess

# Ensure backend root is in pythonpath
backend_root = os.path.dirname(os.path.abspath(__file__))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Auto-detect and use virtual environment python if available
venv_python = os.path.join(backend_root, "venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and sys.executable.lower() != venv_python.lower():
    # Re-execute seamlessly inside the venv
    sys.exit(subprocess.call([venv_python] + sys.argv))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
