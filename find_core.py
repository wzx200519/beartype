import subprocess
import os

res = subprocess.run(["git", "log", "--all", "--", "beartype/_decor/_core.py"], capture_output=True, text=True)
print(res.stdout)
