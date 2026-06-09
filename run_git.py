import os
import subprocess
try:
    with open('/app/beartype-1/git_out.txt', 'w') as f:
        subprocess.run(['git', 'status'], stdout=f, stderr=subprocess.STDOUT)
except Exception as e:
    with open('/app/beartype-1/git_out.txt', 'w') as f:
        f.write(str(e))
