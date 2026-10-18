"""Optional pinned Three.js runtime. No CDN requests during rendering."""
import hashlib
from pathlib import Path
import urllib.request

VERSION = '0.180.0'
FILES = {
    'three.module.min.js': 'e2b5ee6bccd38fd6d8a2428546b83c5f2426d84b152ef82be8055556e3b40eb6',
    'three.core.min.js': '61ba0df005b05991361d040d8ff670e1aadfd0ce7aeebd1fdb0725957a8957de',
    'LICENSE': 'bfe119ea4fd413f5f7ca3fcd63adb0c4a073ed39daa2fe7d3e6b769e21272601',
}


def install():
    target = Path(__file__).resolve().parent / 'vendor/three'
    target.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        dest = target / name
        if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == expected:
            print('verified', name); continue
        suffix = 'LICENSE' if name == 'LICENSE' else 'build/' + name
        data = urllib.request.urlopen(f'https://unpkg.com/three@{VERSION}/{suffix}', timeout=60).read()
        if hashlib.sha256(data).hexdigest() != expected: raise RuntimeError(f'{name}: SHA256 mismatch; no installation')
        tmp = dest.with_suffix('.download'); tmp.write_bytes(data); tmp.replace(dest)
        print('installed', name, len(data))


if __name__ == '__main__': install()
