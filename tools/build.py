#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build static multi-page lesson site from data/book.json

Usage:
  python tools/build.py

It will (re)generate:
  - index.html
  - pages/*.html

Note:
  assets/styles.css and assets/app.js are used as-is.
"""
from __future__ import annotations
import json, html, re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "book.json"
PAGES = ROOT / "pages"

def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s\-آ-ی]+", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "page"

def short_title(t: str, max_len: int = 22) -> str:
    t = (t or "").strip()
    return t if len(t) <= max_len else t[:max_len-1] + "…"

def render_text(t: str) -> str:
    t = (t or "").strip()
    if not t:
        return ""
    return f'<p class="text-gray-700 leading-7 text-sm mt-3">{html.escape(t)}</p>'

def render_list(items, ordered=False, title=None) -> str:
    items = [i for i in (items or []) if isinstance(i, str) and i.strip()]
    if not items:
        return ""
    tag = "ol" if ordered else "ul"
    cls = "list-decimal" if ordered else "list-disc"
    title_html = f'<div class="text-xs text-gray-500 mb-2">{html.escape(title)}</div>' if title else ""
    lis = "\n".join([f'<li class="mb-1">{html.escape(i.strip())}</li>' for i in items])
    return f"""
    <div class="mt-4">
      {title_html}
      <{tag} class="{cls} pr-5 text-sm text-gray-700 space-y-1">
        {lis}
      </{tag}>
    </div>
    """

def render_table(headers, rows, title=None, note=None) -> str:
    headers = headers or []
    rows = rows or []
    if not headers and rows:
        headers = [""] * len(rows[0])
    title_html = f'<div class="font-extrabold mb-3">{html.escape(title)}</div>' if title else ""
    note_html = f'<div class="text-xs text-gray-500 mt-2">{html.escape(note)}</div>' if note else ""
    thead = "".join([f'<th class="p-3 text-right">{html.escape(str(h))}</th>' for h in headers])
    tbody = ""
    for r in rows:
        tds = "".join([f'<td class="p-3 align-top">{html.escape(str(c))}</td>' for c in r])
        tbody += f'<tr class="hover:bg-gray-50">{tds}</tr>'
    return f"""
    <div class="mt-5 overflow-x-auto rounded-2xl border border-gray-200">
      {title_html}
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-700"><tr>{thead}</tr></thead>
        <tbody class="divide-y">{tbody}</tbody>
      </table>
      {note_html}
    </div>
    """

def render_box(style, title, content) -> str:
    style = (style or "note").strip().lower()
    title = (title or "").strip() or "نکته"
    content = (content or "").strip()
    box_class = {"warning":"warn-box", "summary":"diagnosis-box", "note":"good-box"}.get(style, "card")
    return f"""
    <div class="{box_class} p-4 rounded-2xl mt-4">
      <div class="font-extrabold mb-2">{html.escape(title)}</div>
      <div class="text-sm text-gray-700 leading-7">{html.escape(content)}</div>
    </div>
    """

def render_content_item(item: dict) -> str:
    t = (item.get("type") or "").strip()
    if t == "heading":
        lvl = int(item.get("level") or 3)
        txt = (item.get("text") or "").strip()
        if not txt:
            return ""
        tag = "h3" if lvl <= 3 else "h4"
        cls = "text-lg font-black mt-6" if tag == "h3" else "text-base font-extrabold mt-5"
        return f'<{tag} class="{cls}">{html.escape(txt)}</{tag}>'
    if t == "text":
        return render_text(item.get("text") or "")
    if t == "list":
        return render_list(item.get("items") or [], bool(item.get("ordered")), item.get("title"))
    if t == "table":
        return render_table(item.get("headers"), item.get("rows"), item.get("title"), item.get("note"))
    if t == "box":
        return render_box(item.get("style"), item.get("title"), item.get("content"))
    return ""

def render_section(sec: dict) -> str:
    sid = sec.get("id") or slugify(sec.get("title") or "section")
    title = sec.get("title") or ""
    blocks = "\n".join([render_content_item(i) for i in (sec.get("content") or [])])
    return f"""
    <section id="{html.escape(sid)}" class="card p-6 scroll-mt-44">
      <h2 class="section-title text-xl">{html.escape(title)}</h2>
      {blocks}
    </section>
    """

def lesson_filename(seq: int, title: str) -> str:
    return f"{seq:02d}.html"

def build():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    lessons = data.get("lessons") or []
    PAGES.mkdir(exist_ok=True)

    # top nav (lessons)
    chips = []
    for l in lessons:
        seq = int(l.get("seq") or 0)
        title = l.get("title") or ""
        fname = lesson_filename(seq, title)
        label = f"{seq:02d} {short_title(title)}"
        chips.append(f'<a class="navchip" data-page="{fname}" href="{fname}">{html.escape(label)}</a>')
    lesson_nav_html = "\n".join(chips)

    # lesson pages
    for i, l in enumerate(lessons):
        seq = int(l.get("seq") or (i+1))
        title = l.get("title") or ""
        fname = lesson_filename(seq, title)
        prevf = lesson_filename(int(lessons[i-1].get("seq") or i), lessons[i-1].get("title") or "") if i>0 else None
        nextf = lesson_filename(int(lessons[i+1].get("seq") or i+2), lessons[i+1].get("title") or "") if i < len(lessons)-1 else None

        secs = l.get("sections") or []
        sec_links = "".join([f'<a class="navchip" data-section href="#{html.escape(s.get("id") or "")}">{html.escape(s.get("title") or "")}</a>' for s in secs])
        aside = "".join([f'<li><a class="text-blue-700 hover:underline" href="#{html.escape(s.get("id") or "")}">{html.escape(s.get("title") or "")}</a></li>' for s in secs])
        sections_html = "\n".join([render_section(s) for s in secs])

        nav_prev = f'<a class="navchip" href="{prevf}">→ قبلی</a>' if prevf else "<span></span>"
        nav_next = f'<a class="navchip" href="{nextf}">بعدی ←</a>' if nextf else "<span></span>"

        html_page = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>درس {seq}: {html.escape(title)} | درسنامه</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
  <link rel="stylesheet" href="../assets/styles.css" />
</head>
<body class="pb-14" data-page="{fname}">
<header class="gradient-header text-white p-6 shadow-lg sticky top-0 z-50">
  <div class="max-w-6xl mx-auto">
    <div class="breadcrumb text-blue-100/90">
      <a class="underline" href="../index.html">خانه</a> / درس {seq}
    </div>
    <h1 class="text-2xl md:text-3xl font-black mt-2">درس {seq}: {html.escape(title)}</h1>
    <p class="text-blue-100 text-sm mt-1">درسنامه ساختاریافته • مبتنی بر داده‌های JSON</p>
  </div>
</header>

<nav class="max-w-6xl mx-auto p-4 sticky top-[92px] z-40 space-y-2">
  <div class="flex gap-2 overflow-x-auto pb-1 text-sm no-scrollbar bg-white/70 backdrop-blur border border-gray-200 rounded-2xl p-3">
    {lesson_nav_html}
  </div>
  <div class="flex gap-2 overflow-x-auto pb-1 text-sm no-scrollbar bg-white/70 backdrop-blur border border-gray-200 rounded-2xl p-3">
    {sec_links}
  </div>
</nav>

<main class="max-w-6xl mx-auto p-4 space-y-8">
  <div class="grid md:grid-cols-12 gap-4">
    <aside class="md:col-span-4 lg:col-span-3 space-y-4">
      <div class="card p-4">
        <div class="text-xs text-gray-500">نقشه درس</div>
        <ul class="mt-2 text-sm space-y-2">
          {aside}
        </ul>
      </div>
    </aside>

    <div class="md:col-span-8 lg:col-span-9 space-y-8">
      {sections_html}
      <div class="flex justify-between items-center text-sm">
        {nav_prev}
        <a class="navchip" href="../index.html">بازگشت به فهرست</a>
        {nav_next}
      </div>
    </div>
  </div>
</main>

<footer class="text-center text-gray-500 text-xs py-10">
  درسنامه • خروجی چندصفحه‌ای
</footer>
<script src="../assets/app.js"></script>
</body>
</html>
"""
        (PAGES / fname).write_text(html_page, encoding="utf-8")

    # index
    cards = []
    for l in lessons:
        seq = int(l.get("seq") or 0)
        title = l.get("title") or ""
        fname = lesson_filename(seq, title)
        nsec = len(l.get("sections") or [])
        cards.append(f"""
        <a href="pages/{fname}" class="card p-5 block hover:bg-blue-50">
          <div class="flex items-center justify-between gap-3">
            <div>
              <div class="text-xs text-gray-500">درس {seq}</div>
              <div class="text-lg font-black mt-1 text-gray-900">{html.escape(title)}</div>
              <div class="text-xs text-gray-500 mt-2">{nsec} بخش</div>
            </div>
            <div class="w-10 h-10 rounded-2xl bg-blue-100 flex items-center justify-center text-blue-700 font-black">{seq}</div>
          </div>
        </a>
        """)
    index = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>درسنامه | فهرست درس‌ها</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
  <link rel="stylesheet" href="assets/styles.css" />
</head>
<body class="pb-14">

<header class="gradient-header text-white p-6 shadow-lg sticky top-0 z-50">
  <div class="max-w-6xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
      <h1 class="text-2xl md:text-3xl font-black">درسنامه (Multi-page)</h1>
      <p class="text-blue-100 text-sm mt-1">فهرست درس‌ها</p>
    </div>
    <div class="bg-white/15 rounded-2xl p-3 text-xs leading-6">
      <div><span class="font-bold">درس‌ها:</span> {len(lessons)}</div>
      <div><span class="font-bold">ساخته‌شده:</span> {datetime.now().strftime('%Y-%m-%d')}</div>
    </div>
  </div>
</header>

<main class="max-w-6xl mx-auto p-4 space-y-8 mt-4">
  <section class="card p-6">
    <label class="text-xs text-gray-500">جست‌وجو در عنوان درس</label>
    <input id="q" class="mt-2 w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-blue-200"
           placeholder="جست‌وجو..." />
  </section>

  <section>
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-black">درس‌ها</h2>
      <div id="count" class="text-xs text-gray-500"></div>
    </div>
    <div id="grid" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {''.join(cards)}
    </div>
  </section>
</main>

<footer class="text-center text-gray-500 text-xs py-10">
  Static Site Builder
</footer>

<script>
  const q = document.getElementById('q');
  const grid = document.getElementById('grid');
  const count = document.getElementById('count');
  const cards = Array.from(grid.querySelectorAll('a.card'));
  const total = cards.length;
  const norm = s => (s || '').toString().replace(/\s+/g,' ').trim();

  function apply() {{
    const term = norm(q.value).toLowerCase();
    let shown = 0;
    cards.forEach(c => {{
      const t = norm(c.innerText).toLowerCase();
      const ok = !term || t.includes(term);
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    count.textContent = `نمایش ${{shown}} از ${{total}}`;
  }}

  q.addEventListener('input', apply);
  apply();
</script>

</body>
</html>
"""
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("✅ Build complete:", len(lessons), "lessons")

if __name__ == "__main__":
    build()
