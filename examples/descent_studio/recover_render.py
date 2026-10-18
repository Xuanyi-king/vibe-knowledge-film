"""Legacy entry point. Recovery now belongs to engine/render.py."""
from pathlib import Path
import subprocess
import sys
if __name__ == '__main__':
    project=Path(__file__).resolve().parent
    print('Use engine/render.py <project> --resume 4; legacy unverified segments are not imported.')
    subprocess.run([sys.executable,str(project.parents[1]/'engine/render.py'),str(project),'--resume','4',*sys.argv[1:]],check=True)
