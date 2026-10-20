# -*- coding: utf-8 -*-
"""逐帧 seek → 截图 → 管道进 ffmpeg。画面是 t 的纯函数，所以可以只渲一段、只截几帧、乱序截。

  python render.py <工程>                       全片 → <工程>/renders/raw.mp4（无声）
  python render.py <工程> --jobs 4              全片，分 4 段并行渲再无损拼起来（长片用这个）
  python render.py <工程> --resume 4 [--jobs 2] 持久4秒分段；校验后复用，中断后同命令继续
  python render.py <工程> --stills 2.5 8.5 21   只截几帧 → <工程>/review/s_0002.50.png
  python render.py <工程> --sheet 16            全片均匀取 16 帧拼一张 → review/sheet.jpg（开工后先看这个，再渲染）
  python render.py <工程> --sheet 3.5 9 21.5    指定时刻拼一张
  python render.py <工程> --motion 8.2 10.6     一段时间里均匀取 12 帧拼一张 → review/motion_8.2-10.6.jpg（看转场、看动作；后面可以再跟帧数）
  python render.py <工程> --clip 0 12 [名字]    只渲一段 → renders/<名字或_clip>.mp4
  python render.py <工程> --events              导出音效事件表 → audio/events.json（给 audio.py）
  python render.py <工程> --det                 确定性自检：同一批时刻乱序再截一遍，逐字节比
  python render.py <工程> --serve               起本地预览：浏览器开 http://127.0.0.1:8765/?play（←/→ 无，改完刷新）

工程目录里只需要 index.html + film.js。引擎（vk.js、vk-kit.js、fonts/）留在本文件所在目录，
由内置的小服务器挂到 /engine/ 下 —— 不用往每个工程里拷 40MB 字体，也没有 file:// 的跨目录字体限制。
"""
import hashlib, http.server, io, json, math, os, random, subprocess, sys, tempfile, threading
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from . import provenance as provenance
except ImportError:
    import provenance

ENGINE = Path(__file__).resolve().parent
VISUAL_DRAFT = False  # Set only by the restricted preview CLI; never persisted in a project.

class Handler(http.server.SimpleHTTPRequestHandler):
    # Windows registry MIME mappings can label .mjs as text/plain. Modules require JS.
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.js': 'text/javascript', '.mjs': 'text/javascript'}
    proj = None
    def translate_path(self, path):
        p = unquote(urlsplit(path).path)
        root = ENGINE if p.startswith('/engine/') else self.proj
        relative = p[len('/engine/'):] if p.startswith('/engine/') else p.lstrip('/') or 'index.html'
        target = (root / relative).resolve()
        if not target.is_relative_to(root.resolve()): raise ValueError('path leaves served directory')
        return str(target)
    def do_GET(self):
        if self.path.startswith("/favicon"): self.send_response(204); self.end_headers(); return
        try: super().do_GET()
        except ValueError: self.send_error(403, 'Path leaves served directory')
    def do_HEAD(self):
        try: super().do_HEAD()
        except ValueError: self.send_error(403, 'Path leaves served directory')
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
    def log_message(self, *a): pass

class PreviewServer(http.server.ThreadingHTTPServer):
    # Font variants/modules arrive together; Windows can refuse connections
    # when Python 3.12's default five-entry listen queue fills before accept.
    request_queue_size = 64

def serve(proj, port=0):
    h = type("H", (Handler,), {"proj": proj})
    srv = PreviewServer(("127.0.0.1", port), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"

def open_page(p, url):
    # 关掉 LCD 次像素抗锯齿（跳着 seek 字边不抖）；每帧等合成器跑完再截；固定 sRGB
    args = ["--disable-lcd-text", "--run-all-compositor-stages-before-draw", "--force-color-profile=srgb"]
    if os.environ.get('VK_SOFTWARE_GL') == '1':
        args += ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']
    browser = os.environ.get("VK_BROWSER")
    if browser:
        b = p.chromium.launch(executable_path=browser, args=args)
    else:
        try:
            b = p.chromium.launch(channel="chrome", args=args)
        except Exception as exc:
            if "not found" not in str(exc) and "doesn't exist" not in str(exc):
                raise
            b = p.chromium.launch(args=args)  # python -m playwright install chromium
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.on("console", lambda m: m.type in ("error", "warning") and print("[page]", m.text))
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("response", lambda response: errors.append(f"HTTP {response.status}: {response.url}") if response.status >= 400 else None)
    pg._vk_errors = errors
    pg._vk_remote_assets = []
    pg._vk_generated_assets = []
    pg._vk_request_failures = []
    def record_failure(req):
        parsed = urlsplit(req.url)
        location = parsed.path if parsed.hostname in {'127.0.0.1', 'localhost'} else '[nonlocal resource]'
        pg._vk_request_failures.append(f'{req.failure}: {location}')
        del pg._vk_request_failures[:-20]
    pg.on('requestfailed', record_failure)
    def record_request(req):
        if req.url.startswith(url):
            path = unquote(urlsplit(req.url).path).lstrip('/')
            if path.split('/')[0] in {'renders', 'review', 'audio'}: pg._vk_generated_assets.append(path)
        elif not req.url.startswith(('data:', 'blob:')): pg._vk_remote_assets.append(req.url)
    pg.on("request", record_request)
    try:
        if VISUAL_DRAFT:pg.add_init_script('window.__VK_VISUAL_DRAFT__ = true;')
        # Syntax/runtime failures can happen before VK.film installs its READY
        # promise. Surface their cause instead of waiting three minutes.
        pg.add_init_script("""(() => {
          addEventListener('error', e => {
            window.READY_ERROR = e.message || ('Asset failed: ' + (e.target.src || e.target.href || 'unknown'));
          }, true);
          addEventListener('unhandledrejection', e => { window.READY_ERROR = String(e.reason); });
        })();""")
        pg.goto(url)
        pg.wait_for_function("window.READY === true || !!window.READY_ERROR", timeout=180000)
        reason = pg.evaluate("window.READY_ERROR || null")
        if reason or errors:
            failures='; '.join(pg._vk_request_failures[-5:])
            raise RuntimeError((reason or "\n".join(errors))+(f'; failed assets: {failures}' if failures else ''))
    except BaseException:
        b.close()
        raise
    return b, pg

def shot(pg, t):
    if not math.isfinite(t) or t < 0: raise ValueError("frame time must be finite and nonnegative")
    # Capture state with the successful seek, before entering screenshot/compositor.
    # Never issue a second JS diagnostic probe after a timeout: a stuck renderer
    # might also hang that probe. No real-time animation or pixels are changed.
    state = pg.evaluate("""t => {
      seek(t);
      return {ready: window.READY, ready_error: window.READY_ERROR || null,
        document: document.readyState, visibility: document.visibilityState,
        fonts: document.fonts.status, title: String(window.META?.title || '').slice(0,160),
        pending_images: [...document.images].filter(i=>!i.complete).length,
        canvas: [...document.querySelectorAll('canvas')].slice(0,8).map(c=>[c.width,c.height]),
        scene: window.VK_SCENE_INFO || null};
    }""", t)
    if getattr(pg, "_vk_errors", None): raise RuntimeError("\n".join(pg._vk_errors))
    from playwright.sync_api import TimeoutError as CaptureTimeout
    try:
        return pg.screenshot(type="png", timeout=30000)
    except CaptureTimeout as exc:
        diagnostic = dict(time=t, browser=pg.context.browser.version, closed=pg.is_closed(),
                          last_seek_state=state, request_failures=pg._vk_request_failures)
        raise RuntimeError('frame capture timeout (30s; no automatic retry): ' +
                           json.dumps(diagnostic, ensure_ascii=False)) from exc

def with_page(proj, fn):
    from playwright.sync_api import sync_playwright
    srv, url = serve(proj)
    try:
        with sync_playwright() as p:
            b, pg = open_page(p, url)
            try: return fn(pg)
            finally: b.close()
    finally:
        srv.shutdown()
        srv.server_close()

def stills(proj, ts):
    folder=proj/('review/visual-draft' if VISUAL_DRAFT else 'review');folder.mkdir(parents=True,exist_ok=True)
    def go(pg):
        for t in ts: (folder / f"s_{t:07.2f}.png").write_bytes(shot(pg, t))
    with_page(proj, go); print("stills:", len(ts))

def sheet(proj, args, name="sheet"):
    from PIL import Image, ImageDraw, ImageFont
    folder=proj/('review/visual-draft' if VISUAL_DRAFT else 'review');folder.mkdir(parents=True,exist_ok=True)
    def go(pg):
        end = pg.evaluate("END")
        ts = [float(x) for x in args] if len(args) > 1 else [round((i + .5) * end / int(args[0] if args else 16), 2) for i in range(int(args[0] if args else 16))]
        cols = 4 if len(ts) > 6 else 2 if len(ts) > 1 else 1; tw = 1920 // cols; th = tw * 9 // 16
        out = Image.new("RGB", (cols * tw, -(-len(ts) // cols) * th), (20, 20, 20)); d = ImageDraw.Draw(out)
        try: font = ImageFont.truetype(str(ENGINE / "fonts/JetBrainsMono.ttf"), 18)
        except Exception: font = ImageFont.load_default()
        for i, t in enumerate(ts):
            im = Image.open(io.BytesIO(shot(pg, t))).convert("RGB").resize((tw, th), Image.LANCZOS)
            x, y = (i % cols) * tw, (i // cols) * th; out.paste(im, (x, y))
            d.rectangle([x, y + th - 24, x + 78, y + th], fill=(0, 0, 0)); d.text((x + 5, y + th - 22), f"{t:.2f}", font=font, fill=(255, 230, 0))   # 时间标在左下角，不挡左上的年份 / 章节标
        out.save(folder / f"{name}.jpg", quality=90); print("sheet:", folder / f"{name}.jpg", len(ts))
    with_page(proj, go)

def frames(proj, out, a=0.0, b=None, local_only=False):
    sources = provenance.source_files(proj)
    def go(pg):
        end, fps = pg.evaluate("END"), pg.evaluate("FPS")
        if not all(math.isfinite(v) for v in (end, fps, a, end if b is None else b)) or fps <= 0 or end <= 0 or a < 0:
            raise ValueError("invalid duration, fps or clip bounds")
        bb = end if b is None else min(b, end)
        n0, n1 = round(a * fps), round(bb * fps)
        if n1 <= n0: raise ValueError("clip contains no frames")
        out = Path(out_path)
        with tempfile.TemporaryDirectory(prefix=".vk-render-", dir=out.parent) as tmp:
            target = Path(tmp) / "encoded.mp4"
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-threads", "1", "-i", "-",
                                   "-c:v", "libx264", "-threads", "4", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "medium", "-movflags", "+faststart", str(target)], stdin=subprocess.PIPE)
            try:
                for i in range(n0, n1):
                    data = shot(pg, i / fps)
                    if local_only and pg._vk_remote_assets:
                        raise RuntimeError(f"resume requires local assets; download these first: {pg._vk_remote_assets}")
                    if local_only and pg._vk_generated_assets:
                        raise RuntimeError(f"resume inputs cannot use generated renders/review/audio folders; move inputs to assets/: {pg._vk_generated_assets}")
                    ff.stdin.write(data)
                    if (i - n0) % 150 == 0: print(f"  {i - n0}/{n1 - n0}", flush=True)
                ff.stdin.close()
                code = ff.wait(timeout=60)
                if code: raise RuntimeError(f"ffmpeg failed with exit code {code}")
                if not target.is_file() or not target.stat().st_size: raise RuntimeError("ffmpeg produced no video")
                provenance.stable(proj, sources)
                provenance.publish_video(target, out, sources, dict(end=end, fps=fps, start=n0/fps, stop=end if a==0 and bb==end else n1/fps))
            finally:
                if ff.poll() is None:
                    ff.terminate()
                    try: ff.wait(timeout=5)
                    except subprocess.TimeoutExpired: ff.kill(); ff.wait()
                if not ff.stdin.closed: ff.stdin.close()
        print("done", out, f"{(n1 - n0) / fps:.2f}s")
    out_path = out
    with_page(proj, go)

def frames_resume(proj, out, chunk_seconds=4, jobs=1):
    if __package__:
        from .render_cache import render_cached, source_files
    else:
        from render_cache import render_cached, source_files
    from importlib.metadata import version
    def info(pg):
        if pg._vk_remote_assets:
            raise ValueError(f"resume requires local assets: {pg._vk_remote_assets}")
        if pg._vk_generated_assets:
            raise ValueError(f"resume inputs cannot use generated folders; move these to assets/: {pg._vk_generated_assets}")
        meta = pg.evaluate("({end: END, fps: FPS, width: VK.W, height: VK.H, browser: navigator.userAgent, scene: window.VK_SCENE_INFO || null})")
        meta['browser_version'] = pg.context.browser.version
        meta['software_gl'] = os.environ.get('VK_SOFTWARE_GL') == '1'
        return meta
    sources = source_files(proj)
    meta = with_page(proj, info)
    meta['playwright'] = version('playwright')
    return render_cached(proj, out, meta, chunk_seconds, jobs,
                         lambda p, target, a, b: frames(p, target, a, b, local_only=True), expected_sources=sources)

def frames_parallel(proj, out, jobs):
    """Isolated part files; wait for every worker; publish only a successful concat."""
    sources = provenance.source_files(proj)
    end, fps = with_page(proj, lambda pg: (pg.evaluate("END"), pg.evaluate("FPS")))
    if not all(math.isfinite(v) and v > 0 for v in (end, fps)) or jobs < 1:
        raise ValueError("invalid duration, fps or jobs")
    total = round(end * fps)
    if total < 1: raise ValueError("film contains no frames")
    jobs = min(jobs, total)
    cuts = [round(total * i / jobs) for i in range(jobs + 1)]
    with tempfile.TemporaryDirectory(prefix=".vk-parts-", dir=proj / "renders") as tmp:
        folder = Path(tmp)
        parts, procs = [], []
        try:
            for i in range(jobs):
                name = f"{folder.name}/part{i:02d}"
                parts.append(folder / f"part{i:02d}.mp4")
                procs.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(proj), "--clip", repr(cuts[i] / fps), repr(cuts[i + 1] / fps), name],
                                              stdout=subprocess.DEVNULL if i else None))
            codes = [process.wait() for process in procs]
            if any(codes): raise RuntimeError(f"render workers failed: {codes}; run --clip to inspect")
            listing = folder / "parts.txt"
            listing.write_text("".join(f"file '{part.name}'\n" for part in parts), encoding="utf-8")
            target = folder / "joined.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(target)], check=True)
            provenance.stable(proj, sources)
            provenance.publish_video(target, out, sources, dict(end=end, fps=fps, start=0, stop=end))
        finally:
            for process in procs:
                if process.poll() is None:
                    process.terminate()
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired: process.kill(); process.wait()
    print("done", out, f"{total / fps:.2f}s", f"({jobs} workers)")

def events(proj):
    (proj / "audio").mkdir(exist_ok=True)
    sources = provenance.source_files(proj)
    def go(pg):
        ev = pg.evaluate("events()")
        m = pg.evaluate("({end: END, fps: FPS, meta: META, score: window.VK_SCORE?.json() || null})")
        if pg._vk_remote_assets or pg._vk_generated_assets:
            raise RuntimeError('versioned events require local assets outside generated audio/review/renders folders')
        provenance.stable(proj, sources)
        spec = provenance.seal_events(dict(end=m['end'],fps=m['fps'],meta=m['meta'],events=ev,score=m['score']), sources)
        provenance.atomic_json(proj/'audio/events.json', spec)
        print("events:", len(ev), "legacy;", len((m['score'] or {}).get('events', [])), "shared")
    with_page(proj, go)

def det(proj, n=12):
    def go(pg):
        end = pg.evaluate("END"); r = random.Random(7); ts = [round(r.uniform(0, end), 3) for _ in range(n)]
        h1 = {t: hashlib.md5(shot(pg, t)).hexdigest() for t in ts}
        order = ts[:]; r.shuffle(order)
        bad = [t for t in order if hashlib.md5(shot(pg, t)).hexdigest() != h1[t]]
        if bad: raise RuntimeError(f"NOT deterministic at {bad} —— 有东西在跨帧存状态或用了 Math.random()")
        print("deterministic")
    with_page(proj, go)

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if '--visual-draft' in a:
        VISUAL_DRAFT=True;a.remove('--visual-draft')
        if not any(x in a for x in ('--stills','--sheet','--motion','--clip')) or any(x in a for x in ('--resume','--events','--det','--serve','--jobs')):
            sys.exit('--visual-draft is restricted to stills/sheet/motion/clip previews')
        if '--clip' in a and len(a)>a.index('--clip')+3 and a[a.index('--clip')+3]!='draft':
            sys.exit('visual Draft clip must be named draft')
    proj = Path(a[0]).resolve()
    if not (proj / "film.js").exists(): sys.exit(f"{proj} 里没有 film.js")
    (proj / "renders").mkdir(exist_ok=True)
    if "--resume" in a and any(flag in a for flag in ("--clip", "--serve", "--det", "--events", "--motion", "--sheet", "--stills")):
        sys.exit("--resume is a full-film render mode; use it separately from preview/clip/check commands")
    if "--serve" in a:
        srv, url = serve(proj, 8765); print("预览:", url + "?play", "（Ctrl+C 结束）")
        try: threading.Event().wait()
        except KeyboardInterrupt: pass
    elif "--stills" in a: stills(proj, [float(x) for x in a[a.index("--stills") + 1:]])
    elif "--sheet" in a: sheet(proj, a[a.index("--sheet") + 1:])
    elif "--motion" in a:
        i = a.index("--motion"); t0, t1 = float(a[i + 1]), float(a[i + 2]); n = int(a[i + 3]) if len(a) > i + 3 else 12
        sheet(proj, [repr(round(t0 + (t1 - t0) * k / (n - 1), 3)) for k in range(n)], f"motion_{t0:g}-{t1:g}")
    elif "--clip" in a:
        i = a.index("--clip"); name = a[i + 3] if len(a) > i + 3 else "_clip"
        folder=proj/('renders/visual-draft' if VISUAL_DRAFT else 'renders');folder.mkdir(parents=True,exist_ok=True)
        frames(proj, folder / f"{name}.mp4", float(a[i + 1]), float(a[i + 2]))
    elif "--events" in a: events(proj)
    elif "--det" in a: det(proj)
    elif "--resume" in a:
        i = a.index("--resume")
        seconds = float(a[i + 1]) if len(a) > i + 1 and not a[i + 1].startswith("--") else 4
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 1
        frames_resume(proj, proj / "renders/raw.mp4", seconds, jobs)
    elif "--jobs" in a and int(a[a.index("--jobs") + 1]) > 1: frames_parallel(proj, proj / "renders/raw.mp4", int(a[a.index("--jobs") + 1]))
    else: frames(proj, proj / "renders/raw.mp4")
