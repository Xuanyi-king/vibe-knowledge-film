"""Optional geographic renderer/data; pinned local assets, licenses retained."""
import hashlib
from pathlib import Path
import urllib.request

FILES = {'d3-array.min.js': ('https://unpkg.com/d3-array@3.2.4/dist/d3-array.min.js', '80aa70d0cd17dabddf6d056494ea17926a45a69da8b7850220aace331bad671d'), 'd3-geo.min.js': ('https://unpkg.com/d3-geo@3.1.1/dist/d3-geo.min.js', '23e574f1e8d4716d622bce45356a379b66a277162b145f5f147e4c8daefb73d2'), 'd3-array-LICENSE': ('https://unpkg.com/d3-array@3.2.4/LICENSE', '3e6849627f74ff73c257a3ae1efb574015d94fc1035c05ec3c15805165efcbc4'), 'd3-geo-LICENSE': ('https://unpkg.com/d3-geo@3.1.1/LICENSE', '3e3edc1224eec9c39cd26491a21304a62883c1e5b6a65c5283ccc7a6cc94baee'), 'land.geojson': ('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_land.geojson', '9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9'), 'NaturalEarth-LICENSE.md': ('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/ca96624a56bd078437bca8184e78163e5039ad19/LICENSE.md', '2631b5b39b6d1acc56de75235109b5af2dbb4b0ac5a127b6f06185977247fd4b')}

def install():
    target=Path(__file__).resolve().parent/'vendor/geo';target.mkdir(parents=True,exist_ok=True)
    for name,(url,sha) in FILES.items():
        path=target/name
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==sha:
            print('verified',name);continue
        with urllib.request.urlopen(url,timeout=60) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=sha:raise RuntimeError(f'{name}: SHA256 mismatch')
        tmp=path.with_suffix('.download');tmp.write_bytes(data);tmp.replace(path);print('installed',name)

if __name__=='__main__':install()
