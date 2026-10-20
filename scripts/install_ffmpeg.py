"""Pinned Windows CI toolchain from FFmpeg's linked Gyan build distributor.
Caches only the ZIP; checks its publisher SHA256 before every extraction.
"""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import zipfile

VERSION='8.0.1'
PACKAGE=f'ffmpeg-{VERSION}-essentials_build'
URL=f'https://github.com/GyanD/codexffmpeg/releases/download/{VERSION}/{PACKAGE}.zip'
# GitHub release asset 318696612, publisher-provided sha256 digest.
SHA256='e2aaeaa0fdbc397d4794828086424d4aaa2102cef1fb6874f6ffd29c0b88b673'


def digest(path):
    with path.open('rb') as stream:
        result=hashlib.sha256()
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def download(archive):
    if archive.exists() and digest(archive)==SHA256:return archive
    archive.parent.mkdir(parents=True,exist_ok=True)
    archive.unlink(missing_ok=True)
    tmp=archive.with_suffix('.download')
    try:
        for attempt in range(3):
            try:
                with urllib.request.urlopen(URL,timeout=120) as response,tmp.open('wb') as out:
                    shutil.copyfileobj(response,out)
                break
            except OSError:
                if attempt==2:raise
                time.sleep(2)
        if digest(tmp)!=SHA256:raise RuntimeError('FFmpeg ZIP SHA256 mismatch; refusing installation')
        tmp.replace(archive)
    finally:tmp.unlink(missing_ok=True)
    return archive


def install(archive,destination):
    download(archive)
    destination=destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            if not (destination/name).resolve().is_relative_to(destination):
                raise ValueError('FFmpeg archive path leaves installation directory')
        package.extractall(destination)
    folder=destination/PACKAGE/'bin'
    for tool in ('ffmpeg','ffprobe'):
        result=subprocess.run([str(folder/(tool+'.exe')),'-version'],check=True,capture_output=True,
                              text=True,encoding='utf-8',errors='replace')
        if not result.stdout.startswith(f'{tool} version {VERSION}'):
            raise RuntimeError(f'unexpected {tool} version: {result.stdout[:120]}')
        print(result.stdout.splitlines()[0],flush=True)
    if os.environ.get('GITHUB_PATH'):
        with open(os.environ['GITHUB_PATH'],'a',encoding='utf-8') as stream:stream.write(str(folder)+'\n')
    print('FFmpeg bin:',folder,flush=True)
    return folder


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    args=p.parse_args()
    if os.name!='nt':p.error('this pinned executable build is for Windows')
    install(args.archive,args.destination)
