import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / 'pages'

def process_file(path: Path):
    text = path.read_text(encoding='utf-8')
    if 'id="global-sidebar"' in text:
        print(f'SKIP (already patched): {path.name}')
        return False
    b_idx = text.find('<body')
    if b_idx == -1:
        print('No <body> tag in', path.name)
        return False
    # find end of body start tag
    end_body_tag = text.find('>', b_idx)
    if end_body_tag == -1:
        print('Malformed body tag in', path.name)
        return False
    main_idx = text.find('<main', end_body_tag)
    if main_idx == -1:
        print('No <main> tag in', path.name)
        return False
    # extract original header region for title extraction
    mid = text[end_body_tag+1:main_idx]
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', mid, re.S)
    if h1_match:
        h1_text = h1_match.group(1).strip()
    else:
        # fallback to filename without extension
        h1_text = path.stem
    new_mid = (
        '\n<header class="gradient-header text-white p-6 shadow-lg sticky top-0 z-50">\n'
        '  <div class="max-w-6xl mx-auto flex items-center justify-between">\n'
        f'    <div>\n      <h1 class="text-2xl md:text-3xl font-black">{h1_text}</h1>\n'
        '      <p id="page-subtitle" class="text-blue-100 text-sm mt-1">درسنامه ساختاریافته</p>\n'
        '    </div>\n'
        '    <button id="sidebarToggle" class="sidebar-toggle-btn">فهرست</button>\n'
        '  </div>\n'
        '</header>\n\n'
        '<div id="global-sidebar" class="sidebar-root" aria-hidden="true"></div>\n\n'
    )
    new_text = text[:end_body_tag+1] + new_mid + text[main_idx:]
    path.write_text(new_text, encoding='utf-8')
    print('Patched:', path.name)
    return True

if __name__ == '__main__':
    modified = []
    for i in range(7, 44):
        fname = f'{i:02d}.html'
        p = PAGES_DIR / fname
        if not p.exists():
            print('Missing file', fname)
            continue
        if process_file(p):
            modified.append(fname)
    print('\nDone. Modified files:\n' + '\n'.join(modified))
