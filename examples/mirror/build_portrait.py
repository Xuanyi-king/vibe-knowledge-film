"""Rebuild the CC0 bust data, without installing MakeHuman or Blender.
python examples/mirror/build_portrait.py
Only the explicitly CC0 graphical base mesh is used, not AGPL program code.
"""
import hashlib,json,urllib.request
from pathlib import Path
REV='3c701a8e52f09e69922e8b598d23be2d7dfc49e3'
URL=f'https://raw.githubusercontent.com/makehumancommunity/makehuman/{REV}/makehuman/data/3dobjs/base.obj'
EXPECTED='8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c'

def build(data):
    vertices=[];faces=[];group=''
    for line in data.decode().splitlines():
        if line.startswith('v '):vertices.append(list(map(float,line.split()[1:4])))
        elif line.startswith('g '):group=line[2:]
        elif line.startswith('f ') and group=='body':
            f=[int(x.split('/')[0])-1 for x in line[2:].split()]
            if all(vertices[i][1]>5.3 for i in f):
                for i in range(1,len(f)-1):faces.append([f[0],f[i],f[i+1]])
    ids=sorted(set(i for f in faces for i in f));mapping={old:i for i,old in enumerate(ids)}
    # MakeHuman decimetres -> metres; face centre becomes the local origin.
    positions=[[round(vertices[i][0]*.1,6),round((vertices[i][1]-7.1)*.1,6),round(vertices[i][2]*.1,6)] for i in ids]
    def near(target):return min(range(len(positions)),key=lambda i:sum((a-b)**2 for a,b in zip(positions[i],target)))
    landmarks={name:[near([-x,y,z]),near([x,y,z])] for name,x,y,z in [('nose',.02034,-.01397,.14628),('cheek',.06,-.012,.113)]}
    return {'positions':positions,'triangles':[[mapping[i] for i in f] for f in faces],'landmarks':landmarks,'source':URL,'source_sha256':hashlib.sha256(data).hexdigest(),'license':'CC0-1.0 / MakeHuman hm08 base graphical mesh, asset header explicitly released September 2020','note':'Illustrative bust, not a participant, photograph, or replica of the 2018 average-face model.'}

def main():
    data=urllib.request.urlopen(URL,timeout=60).read()
    if hashlib.sha256(data).hexdigest()!=EXPECTED:raise ValueError('portrait source SHA256 mismatch')
    p=Path(__file__).parent/'assets/portrait.json';p.write_text(json.dumps(build(data),separators=(',',':'))+'\n');print(p,p.stat().st_size)
if __name__=='__main__':main()
