# -*- coding: utf-8 -*-
"""建一个新片工程：
  python new_film.py <工程目录> --world C|B|custom --duration <完整剧本秒数> [--force]
C/B旧工程保持兼容；本系列默认暗金深沉，custom是自绘实现入口。外观见 references/worlds.md。

工程里是 index.html 和一份只能跑起来的 film.js 骨架——里面一行画面都没有。
文案不同，屏上的东西就不同，代码也不同：每一镜按当前镜头记录现写，不要从别的片子里搬画面。
引擎留在 skill 目录里，由 engine/render.py 挂载。"""
import argparse, json, math, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLD = {   # 外观名、theme、字幕样式、色板、这套外观的常驻元素（都在 vk-kit.js，用法见 references/engine.md）
    "CUSTOM": ("自绘实现", "flat", "flat", "flat", "保持已定暗金外观，按storyboard.md现写主体；不套仪表或星点"),
    "B": ("B 寓言", "flat", "flat", "flat", "仪表 K.gauge、片名卡 K.titleGilt；场景自己画进 fr.look.under"),
    "C": ("C 夜曲", "night", "night", "night", "章节标 K.chapterMark、片名卡 K.titleNight；字幕带一行英文（en）"),
}
SKELETON = """/* ★ 片名 · {name}
 * 这是骨架，一行画面都没有。先完成storyboard.md的完整字幕稿与分镜，再按它逐镜现写。
 * 每个场景的函数头上先写一行：这是什么（日常的词）/ 它在干什么（一个动词）/ 观众明白了什么。
 * 事实和出处、哪些是示意，写在review/notes.md；代码注释不能代替剧本和分镜。
 * 这套外观的常驻元素：{standing}。规格见 references/worlds.md。 */
(function () {{
'use strict';
const {{ W, H, clamp, lerp, seg, smooth, ss, E, fade, hash, rng, rgba, mix }} = VK;
const K = VKit, P = K.PAL.{pal};

const T = {{ end: {duration} }};                            // 由叙事决定，可随试画修改，不是默认交付时长
const SUBS = [                                             // 一句字幕一行，和分镜表对着写；{{词}} 金色，{{!词}} 红色
  // {{ a: 0.8, b: 4.2, zh: '……'{en} }},
];

/* 一个场景一个函数，自己管自己的进场和退场。 */
function scene1(fr, t) {{
}}

VK.film({{
  dur: T.end, theme: '{theme}', {look}meta: {{ title: '' }},
  draw(fr, t) {{
    scene1(fr, t);
    K.subs(fr, t, SUBS, '{subs}');                         // 字幕永远最后画，压在一切之上
  }},
}});
}})();
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--world', required=True, type=str.upper, choices=WORLD,
                        help='按已定风格选实现入口；本系列暗金方向可用custom，旧B/C兼容')
    parser.add_argument('--duration', type=float, help='Agent预计的全片正数秒数，可随叙事修改')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--series',choices=['shape-of-luck'],help='lock new series music to its reviewed master; missing assets block production')
    a = parser.parse_args()
    world = a.world
    duration = a.duration
    if duration is None:
        if world == 'CUSTOM': parser.error('提供 --duration 预计全片时长，可在试画后修改；不要机械填30')
        duration = 30
        print('兼容旧B/C命令：30秒仅为历史骨架占位。正式创作请按当前叙事用 --duration 预计全片时长，并随试画迭代。', file=sys.stderr)
    if not math.isfinite(duration) or duration <= 0:
        parser.error('--duration 必须是有限正数秒数')
    proj = a.project.resolve()
    proj.mkdir(parents=True, exist_ok=True)
    film = proj / "film.js"
    if film.exists() and not a.force: sys.exit(f"{film} 已经存在。要覆盖加 --force")
    if a.series and (proj/'music.json').exists():sys.exit('series scaffold does not overwrite existing music.json; edit its policy explicitly')
    name, theme, subs, pal, standing = WORLD[world]
    shutil.copy(ROOT / "engine/index.html", proj / "index.html")
    film.write_text(SKELETON.format(name=name, duration=format(duration, '.15g'), theme=theme, subs=subs, pal=pal, standing=standing, look="bloom: 0, grain: 0, " if world == "CUSTOM" else "", en=", en: '……'" if world == "C" else ""), encoding="utf-8", newline="\n")
    if a.series:
        code=film.read_text(encoding='utf-8')
        film.write_text("Promise.all([window.__VK_VISUAL_DRAFT__===true ? Promise.resolve({MUSIC:null}) : import('./assets/music-plan.mjs'),import('/engine/vk-motion.mjs')]).then(([{MUSIC},{score}])=>{\n"
            +f"if(window.__VK_VISUAL_DRAFT__!==true && (MUSIC.selected!=='signature'||MUSIC.signature?.id!=={json.dumps(a.series)}))throw Error('series master missing/mismatched; no fallback');\n"
            +f"window.VK_SCORE=score({{end:{duration},events:[...(MUSIC ? MUSIC.events : [])]}}); // Add this film's SFX/ambience events here.\n"
            +code+'\n});\n',encoding='utf-8')
        (proj/'music.json').write_text(json.dumps({'mode':'signature','end':duration,
            'src':'assets/private-music/master.wav','source_sha256':None,
            'signature':{'id':a.series,'required':True,'index':'assets/private-music/master-index.json','index_sha256':None},
            'rights':{'scope':'unavailable'},'clips':[],'anchors':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if world == "CUSTOM" and not (proj / "direction.md").exists():
        (proj / "direction.md").write_text("# 作品方向\n\n默认保持《运气的形状》的暗金深沉气质，只有用户明确改方向才更换美术。custom只表示自绘，不是随题目另选风格。先完成storyboard.md中的全片字幕稿与逐镜动作；事实/来源另记review/notes.md。\n\n- 母题与首尾理解变化：\n- 颜色：近黑深空间、暖白实体、少量暗金与朱红，各有稳定含义。\n- 字体：主字幕与片名用中文衬线；flat默认字幕需要按此调整。\n- 构图与机位：服务注意力，不连续缓慢放大整片。\n- 光源、材质与空间：同一世界，实物可辨。\n- 声音：指定音乐为主，少量必要拟音，允许动作安静。\n", encoding="utf-8")
    render = ROOT / "engine/render.py"
    print(f"建好了：{proj}（{name}）\n"
          f"  预览  python \"{render}\" \"{proj}\" --serve\n"
          f"  拼图  python \"{render}\" \"{proj}\" --sheet 16\n"
          f"  渲染  python \"{render}\" \"{proj}\"\n"
          f"下一步：先完成storyboard.md的完整字幕稿与逐镜分镜，再写最需要验证的一镜；确认实际画面后继续全片。")
