"""Entrypoint inside official test container; no user browser/profile access."""
import os
import subprocess
import sys

subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check',
                '--target=/deps','playwright==1.65.2'],check=True)
os.execv(sys.executable,[sys.executable,'-m','playwright','run-server','--host','0.0.0.0','--port','3000'])
