#!/usr/bin/env python3
"""
md2slides.py — Convert section Markdown files into a standalone HTML presentation.

Usage
-----
# Build all sections (section1.md … sectionN.md found in current dir)
python3 md2slides.py

# Build specific files
python3 md2slides.py section1.md section2.md

# Choose output filename
python3 md2slides.py -o my-slides.html

# Embed all Markdown content so the HTML works offline / from file://
python3 md2slides.py --embed          (default: always embed)

# Write a minimal HTML that still fetches .md files at runtime
python3 md2slides.py --no-embed

Options
-------
  -o / --output    Output filename         [default: index.html]
  --embed          Embed MD in JS          [default: True]
  --no-embed       Fetch MD at runtime     (requires HTTP server)
  --title          Browser tab title       [default: from first h1]
  --author         Override author string
  -h / --help      Show this message
"""

import argparse
import glob
import os
import re
import sys
import textwrap
from pathlib import Path

# ── Version ──────────────────────────────────────────────────────────────────
__version__ = "1.0.0"

# ── Section metadata heuristics ──────────────────────────────────────────────
def guess_label(filename: str, content: str, index: int) -> dict:
    """Derive display label and chip text from filename + first h1."""
    # Try to extract first h1
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    h1 = h1_match.group(1).strip() if h1_match else Path(filename).stem

    # Short label for the tab: "N · Title (truncated)"
    short = h1[:28] + '…' if len(h1) > 30 else h1
    label = f"{index + 1} · {short}"

    # Chip: shown on every slide of this section
    chip = f"Part {index + 1} · {h1}"

    return {"file": filename, "label": label, "chip": chip, "h1": h1}


# ── JS string escaping ────────────────────────────────────────────────────────
def js_escape(s: str) -> str:
    """Escape a string for embedding inside a JS template literal."""
    s = s.replace('\\', '\\\\')
    s = s.replace('`',  '\\`')
    s = s.replace('$',  '\\$')
    return s


# ── Read files ────────────────────────────────────────────────────────────────
def collect_sections(paths: list[str]) -> list[dict]:
    sections = []
    for i, path in enumerate(paths):
        p = Path(path)
        if not p.exists():
            print(f"[warning] {path} not found — skipping", file=sys.stderr)
            continue
        content = p.read_text(encoding='utf-8')
        meta = guess_label(p.name, content, i)
        meta['content'] = content
        sections.append(meta)
    if not sections:
        sys.exit("[error] No input files found.")
    return sections


# ── CSS (identical to index.html) ────────────────────────────────────────────
CSS = """\
:root{
  --bg:#0e0f11;--surface:#16181c;--border:#2a2d35;
  --accent:#c8b560;--accent2:#7eb8c9;
  --text:#e8e4d8;--muted:#7a7870;--code-bg:#1c1f26;
  --font-head:'Playfair Display',Georgia,serif;
  --font-body:'IBM Plex Sans','Helvetica Neue',sans-serif;
  --font-mono:'IBM Plex Mono','Courier New',monospace;
}
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);font-weight:300;font-size:16px;line-height:1.6;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#topbar{display:flex;align-items:center;justify-content:space-between;padding:0 20px;border-bottom:0.5px solid var(--border);background:var(--surface);flex-shrink:0;height:44px;gap:16px}
#course-label{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);white-space:nowrap;flex-shrink:0}
#section-tabs{display:flex;gap:2px;flex:1;justify-content:center;height:100%;align-items:stretch}
.sec-tab{background:none;border:none;color:var(--muted);font-family:var(--font-mono);font-size:11px;letter-spacing:.06em;padding:0 14px;cursor:pointer;border-bottom:2px solid transparent;transition:color .15s,border-color .15s;white-space:nowrap}
.sec-tab:hover{color:var(--text)}
.sec-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
#right-bar{display:flex;align-items:center;gap:12px;flex-shrink:0}
#slide-counter{font-family:var(--font-mono);font-size:11px;color:var(--muted);white-space:nowrap}
#progress-bar{width:80px;height:2px;background:var(--border);border-radius:1px;overflow:hidden}
#progress-fill{height:100%;background:var(--accent);border-radius:1px;transition:width .3s ease}
#stage{flex:1;display:flex;align-items:stretch;overflow:hidden;position:relative}
.slide{position:absolute;inset:0;padding:52px 80px 40px;display:flex;flex-direction:column;justify-content:center;opacity:0;transform:translateX(40px);transition:opacity .28s ease,transform .28s ease;pointer-events:none;overflow-y:auto}
.slide.active{opacity:1;transform:translateX(0);pointer-events:auto}
@media(min-width:900px){.slide{padding:58px 100px 46px}}
.section-label{font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);margin-bottom:24px;font-family:var(--font-mono);flex-shrink:0}
.slide-title{background:var(--surface)}
.slide-title h1{font-family:var(--font-head);font-size:clamp(26px,3.2vw,44px);font-weight:400;line-height:1.2;color:var(--text);max-width:820px;margin-bottom:24px}
.slide-title .rule{width:56px;height:2px;background:var(--accent);margin:20px 0}
.slide-title p{font-size:14px;color:var(--muted)}
.slide-title strong{color:var(--accent2);font-weight:400}
.slide-quote{background:var(--surface)}
.slide-quote blockquote{border-left:3px solid var(--accent);padding-left:28px;margin:0 0 20px;max-width:780px}
.slide-quote blockquote p{font-family:var(--font-head);font-size:clamp(16px,1.9vw,23px);font-style:italic;color:var(--text);line-height:1.55}
.slide-quote blockquote p em{color:var(--accent);font-style:normal}
.slide h2{font-family:var(--font-head);font-size:clamp(20px,2.6vw,34px);font-weight:400;color:var(--text);margin-bottom:28px;line-height:1.25;border-bottom:0.5px solid var(--border);padding-bottom:14px;flex-shrink:0}
.slide p{font-size:clamp(13px,1.45vw,17px);line-height:1.7;color:var(--text);max-width:780px;margin-bottom:14px}
.slide p em{color:var(--accent);font-style:italic}
.slide p strong{color:var(--accent2);font-weight:500}
.slide p>em:only-child{font-size:12px;color:var(--muted);font-style:normal;font-family:var(--font-mono);display:block;margin-top:-6px;margin-bottom:14px}
.slide blockquote{border-left:3px solid var(--accent);padding-left:22px;margin:0 0 18px;max-width:780px}
.slide blockquote p{font-family:var(--font-head);font-size:clamp(13px,1.5vw,18px);font-style:italic;color:var(--text);line-height:1.5;margin-bottom:6px}
.slide blockquote p em{color:var(--accent);font-style:normal}
.slide ul,.slide ol{padding-left:20px;max-width:780px;margin-bottom:18px}
.slide li{font-size:clamp(13px,1.4vw,16px);line-height:1.7;margin-bottom:9px;color:var(--text)}
.slide li strong{color:var(--accent2);font-weight:500}
.slide li em{color:var(--accent);font-style:italic}
.slide ul li::marker{color:var(--accent)}
.slide pre{background:var(--code-bg);border:0.5px solid var(--border);border-left:3px solid var(--accent2);border-radius:6px;padding:18px 22px;margin:0 0 18px;overflow-x:auto;max-width:860px;flex-shrink:0}
.slide pre code{font-family:var(--font-mono);font-size:clamp(10px,1vw,13px);line-height:1.65;color:#a8c4cc}
.slide code:not(pre code){font-family:var(--font-mono);font-size:.87em;background:var(--code-bg);border:0.5px solid var(--border);padding:1px 5px;border-radius:3px;color:var(--accent2)}
.slide table{border-collapse:collapse;width:100%;max-width:860px;margin-bottom:18px;font-size:clamp(11px,1.2vw,14px)}
.slide th{background:var(--code-bg);color:var(--accent);font-weight:500;font-family:var(--font-mono);font-size:.84em;letter-spacing:.04em;padding:9px 13px;text-align:left;border-bottom:1px solid var(--border)}
.slide td{padding:8px 13px;border-bottom:0.5px solid var(--border);color:var(--text);vertical-align:top}
.slide tr:last-child td{border-bottom:none}
.slide tr:hover td{background:rgba(200,181,96,.04)}
.slide-summary h2{color:var(--accent)}
.slide-refs h2{font-size:18px;color:var(--muted)}
.slide-refs li{font-size:12px;color:var(--muted);margin-bottom:5px;line-height:1.5}
#navbar{display:flex;align-items:center;justify-content:space-between;padding:10px 24px;border-top:0.5px solid var(--border);background:var(--surface);flex-shrink:0}
.nav-btn{background:none;border:0.5px solid var(--border);color:var(--muted);font-family:var(--font-mono);font-size:12px;padding:5px 16px;border-radius:4px;cursor:pointer;letter-spacing:.06em;transition:color .15s,border-color .15s,background .15s}
.nav-btn:hover:not(:disabled){color:var(--text);border-color:var(--accent);background:rgba(200,181,96,.06)}
.nav-btn:disabled{opacity:.22;cursor:default}
#kbd-hint{font-family:var(--font-mono);font-size:11px;color:var(--muted);letter-spacing:.04em;text-align:center}
#footer-license{font-family:var(--font-mono);font-size:10px;color:var(--muted);letter-spacing:.04em;text-align:right;padding:0 24px;flex-shrink:0}
#footer-license a{color:var(--muted);text-decoration:underline;text-underline-offset:2px}
#footer-license a:hover{color:var(--accent)}
#loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--font-mono);font-size:13px;color:var(--muted);letter-spacing:.08em}
.slide::-webkit-scrollbar{width:3px}
.slide::-webkit-scrollbar-track{background:transparent}
.slide::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
"""

# ── JS runtime ────────────────────────────────────────────────────────────────
JS_RUNTIME = """\
function parseSlides(md){return md.split(/\\n---\\n/).map(s=>s.trim()).filter(Boolean);}
function classify(html,idx){
  if(idx===0)return 'slide-title';
  if(html.includes('<blockquote>')&&!html.includes('<h2>'))return 'slide-quote';
  if(/Summary/.test(html))return 'slide-summary';
  if(/References/.test(html))return 'slide-refs';
  return '';
}
function buildSlide(raw,idx,si){
  const html=marked.parse(raw);
  const cls=classify(html,idx);
  const div=document.createElement('div');
  div.className='slide'+(cls?' '+cls:'');
  const chip=document.createElement('div');
  chip.className='section-label';
  chip.textContent=SECTIONS[si].chip;
  if(cls==='slide-title'){
    const tmp=document.createElement('div');tmp.innerHTML=html;
    const h1=tmp.querySelector('h1');
    div.appendChild(chip);
    if(h1)div.appendChild(h1);
    const rule=document.createElement('div');rule.className='rule';div.appendChild(rule);
    [...tmp.children].forEach(el=>div.appendChild(el));
  }else{
    div.appendChild(chip);
    const c=document.createElement('div');c.innerHTML=html;div.appendChild(c);
  }
  return div;
}
async function fetchMd(file){
  try{const r=await fetch(file);if(!r.ok)throw 0;return await r.text();}
  catch{return FALLBACKS[file]||`## Coming soon\\n\\nThis section is not yet available.`;}
}
async function loadSection(idx){
  if(sections[idx])return;
  const md=await fetchMd(SECTIONS[idx].file);
  const stage=document.getElementById('stage');
  sections[idx]=parseSlides(md).map((raw,i)=>{
    const s=buildSlide(raw,i,idx);
    s.style.display='none';
    stage.appendChild(s);
    return s;
  });
}
function showSlide(si,ii,dir){
  const cur=sections[currentSection]?.[currentSlide];
  if(cur){
    cur.classList.remove('active');
    cur.style.opacity='0';
    cur.style.transform=dir>=0?'translateX(-40px)':'translateX(40px)';
    setTimeout(()=>{cur.style.opacity='';cur.style.transform='';cur.style.display='none';},300);
  }
  currentSection=si;currentSlide=ii;
  const next=sections[si][ii];
  next.style.display='';
  if(dir!==0){
    next.style.opacity='0';
    next.style.transform=dir>=0?'translateX(40px)':'translateX(-40px)';
    requestAnimationFrame(()=>requestAnimationFrame(()=>{next.style.opacity='';next.style.transform='';}));
  }
  next.classList.add('active');
  const total=sections[si].length;
  document.getElementById('slide-counter').textContent=`${ii+1} / ${total}`;
  document.getElementById('progress-fill').style.width=(total>1?(ii/(total-1))*100:100)+'%';
  document.getElementById('btn-prev').disabled=si===0&&ii===0;
  document.getElementById('btn-next').disabled=si===SECTIONS.length-1&&ii===total-1;
  document.querySelectorAll('.sec-tab').forEach((t,i)=>t.classList.toggle('active',i===si));
}
async function go(delta){
  let s=currentSection,i=currentSlide+delta;
  if(i<0){s--;if(s<0)return;await loadSection(s);i=sections[s].length-1;}
  else if(i>=sections[currentSection].length){s++;if(s>=SECTIONS.length)return;await loadSection(s);i=0;}
  showSlide(s,i,delta);
}
async function jumpSection(idx){
  if(idx===currentSection)return;
  await loadSection(idx);
  showSlide(idx,0,idx>currentSection?1:-1);
}
function buildTabs(){
  const nav=document.getElementById('section-tabs');
  SECTIONS.forEach((sec,i)=>{
    const btn=document.createElement('button');
    btn.className='sec-tab';btn.textContent=sec.label;
    btn.addEventListener('click',()=>jumpSection(i));
    nav.appendChild(btn);
  });
}
document.addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown',' '].includes(e.key)){e.preventDefault();go(1);}
  if(['ArrowLeft','ArrowUp'].includes(e.key)){e.preventDefault();go(-1);}
  if(e.key==='f'||e.key==='F')document.documentElement.requestFullscreen?.();
  if(e.key>='1'&&e.key<='9')jumpSection(parseInt(e.key)-1);
});
document.getElementById('btn-next').addEventListener('click',()=>go(1));
document.getElementById('btn-prev').addEventListener('click',()=>go(-1));
let tx=null;
document.addEventListener('touchstart',e=>{tx=e.touches[0].clientX;});
document.addEventListener('touchend',e=>{if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>40)go(dx<0?1:-1);tx=null;});
(async()=>{
  buildTabs();
  document.getElementById('loading').remove();
  await loadSection(0);
  showSlide(0,0,0);
  if(SECTIONS.length>1)loadSection(1).catch(()=>{});
})();
"""

# ── HTML template ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="license" content="CC BY-NC 4.0 — https://creativecommons.org/licenses/by-nc/4.0/">
<meta name="author" content="{author}">
<title>{title}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<style>
{css}
</style>
</head>
<body>

<div id="topbar">
  <span id="course-label">{course_label}</span>
  <nav id="section-tabs" aria-label="Sections"></nav>
  <div id="right-bar">
    <span id="slide-counter">— / —</span>
    <div id="progress-bar"><div id="progress-fill" style="width:0%"></div></div>
  </div>
</div>

<div id="stage">
  <div id="loading">Loading slides\u2026</div>
</div>

<div id="navbar">
  <button class="nav-btn" id="btn-prev" disabled>\u2190 prev</button>
  <span id="kbd-hint">\u2190 \u2192 arrow keys &nbsp;\u00b7&nbsp; 1\u2013{n_sections} switch section &nbsp;\u00b7&nbsp; F fullscreen</span>
  <button class="nav-btn" id="btn-next" disabled>next \u2192</button>
</div>

<div id="footer-license">
  <a href="https://creativecommons.org/licenses/by-nc/4.0/" target="_blank" rel="noopener">
    CC BY-NC 4.0
  </a>
  &nbsp;\u00b7&nbsp; {author} &nbsp;\u00b7&nbsp; {year}
</div>

<script>
// ── Section manifest (generated by md2slides.py {version}) ──
const SECTIONS = {sections_json};

let currentSection = 0, currentSlide = 0;
let sections = [];

{js_runtime}

// ── Embedded Markdown content ──
const FALLBACKS = {{{fallbacks}}};
</script>
</body>
</html>
"""


# ── Build output ──────────────────────────────────────────────────────────────
def build_html(sections_meta: list[dict], args) -> str:
    import json
    from datetime import date

    # Derive title from first h1 of first section if not given
    title = args.title
    if not title:
        title = sections_meta[0].get('h1', 'Slides')

    author = args.author or "Dr. Ludovica Pannitto — Università di Bologna"
    year   = str(date.today().year)

    # Course label: everything before the first dash in title, or full title
    course_label = re.split(r'\s*[—–-]\s*', title)[0].strip()
    if len(course_label) > 40:
        course_label = course_label[:37] + '…'

    # Sections JSON for JS
    sections_js = [
        {"file": s["file"], "label": s["label"], "chip": s["chip"]}
        for s in sections_meta
    ]
    sections_json = json.dumps(sections_js, ensure_ascii=False, indent=2)

    # Fallbacks dict
    if args.embed:
        fallback_parts = []
        for s in sections_meta:
            key = js_escape(s['file'])
            val = js_escape(s['content'])
            fallback_parts.append(f"  {json.dumps(s['file'])}: `{val}`")
        fallbacks = '\n' + ',\n'.join(fallback_parts) + '\n'
    else:
        fallbacks = ''

    html = HTML_TEMPLATE.format(
        css=CSS,
        title=title,
        author=author,
        year=year,
        course_label=course_label,
        n_sections=len(sections_meta),
        sections_json=sections_json,
        js_runtime=JS_RUNTIME,
        fallbacks=fallbacks,
        version=__version__,
    )
    return html


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument('files', nargs='*', metavar='FILE',
                   help='Markdown files to include (default: section*.md in current dir)')
    p.add_argument('-o', '--output', default='index.html',
                   help='Output HTML filename (default: index.html)')
    p.add_argument('--title', default='',
                   help='Browser tab title (default: first h1 of first file)')
    p.add_argument('--author', default='',
                   help='Author string shown in footer (default: Dr. Ludovica Pannitto)')
    p.add_argument('--embed', dest='embed', action='store_true', default=True,
                   help='Embed Markdown in JS fallbacks (default: True)')
    p.add_argument('--no-embed', dest='embed', action='store_false',
                   help='Do not embed Markdown; fetch at runtime (requires HTTP server)')
    p.add_argument('--version', action='version', version=f'md2slides {__version__}')
    return p.parse_args()


def main():
    args = parse_args()

    # Resolve input files
    if args.files:
        input_files = args.files
    else:
        # Auto-discover section*.md in cwd, sorted
        input_files = sorted(glob.glob('section*.md'))
        if not input_files:
            sys.exit(
                "[error] No section*.md files found in current directory.\n"
                "Pass filenames explicitly or run from the slides directory."
            )

    print(f"md2slides {__version__}")
    print(f"  Input:  {', '.join(input_files)}")
    print(f"  Output: {args.output}")
    print(f"  Embed:  {args.embed}")

    sections_meta = collect_sections(input_files)
    html = build_html(sections_meta, args)

    out_path = Path(args.output)
    out_path.write_text(html, encoding='utf-8')

    size_kb = out_path.stat().st_size / 1024
    print(f"  Done:   {out_path} ({size_kb:.1f} KB, {len(sections_meta)} section(s))")
    print()
    print("  To view locally:")
    print("    python3 -m http.server 8000")
    print("    open http://localhost:8000/" + args.output)


if __name__ == '__main__':
    main()
