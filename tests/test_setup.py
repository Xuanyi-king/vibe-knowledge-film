"""Pinned Windows download integrity and real FFmpeg toolchain smoke."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


class InstallerTest(unittest.TestCase):
    def test_verified_cache_reused_and_corrupt_cache_replaced(self):
        from scripts import install_ffmpeg as installer
        payload=b'fixed archive fixture';expected=hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as d,patch.object(installer,'SHA256',expected):
            path=Path(d)/'ffmpeg.zip';path.write_bytes(payload)
            with patch.object(installer.urllib.request,'urlopen',side_effect=AssertionError('cached download')):
                self.assertEqual(installer.download(path),path)
            path.write_bytes(b'corrupt cached bytes')
            with patch.object(installer.urllib.request,'urlopen',return_value=io.BytesIO(payload)) as get:
                installer.download(path)
            self.assertEqual(path.read_bytes(),payload);self.assertEqual(get.call_count,1)

    def test_wrong_download_digest_is_never_installed(self):
        from scripts import install_ffmpeg as installer
        with tempfile.TemporaryDirectory() as d,patch.object(installer.urllib.request,'urlopen',return_value=io.BytesIO(b'not the release')):
            path=Path(d)/'ffmpeg.zip'
            with self.assertRaisesRegex(RuntimeError,'SHA256'):installer.download(path)
            self.assertFalse(path.exists());self.assertFalse(path.with_suffix('.download').exists())

    def test_network_retries_are_bounded(self):
        from scripts import install_ffmpeg as installer
        with tempfile.TemporaryDirectory() as d,patch.object(installer.time,'sleep') as sleep:
            with patch.object(installer.urllib.request,'urlopen',side_effect=OSError('upstream unavailable')) as get:
                with self.assertRaises(OSError):installer.download(Path(d)/'ffmpeg.zip')
            self.assertEqual(get.call_count,3);self.assertEqual(sleep.call_count,2)


class ToolchainTest(unittest.TestCase):
    def test_real_encode_probe_decode_in_unicode_path(self):
        for tool in ('ffmpeg','ffprobe'):
            r=subprocess.run([tool,'-version'],check=True,capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertTrue(r.stdout.startswith(tool+' version'),r.stdout+r.stderr)
        with tempfile.TemporaryDirectory(prefix="vk 工程 space '") as d:
            video=Path(d)/'编码 test.mp4'
            subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=blue:s=64x64:r=30',
                            '-frames:v','3','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(video)],check=True)
            data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
            stream=data['streams'][0]
            self.assertEqual((stream['width'],stream['height'],int(stream['nb_frames'])),(64,64,3))
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
