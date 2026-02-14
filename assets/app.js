
(() => {
  const chapters = [
    {
      title: 'فصل ۱: رویکرد بالینی به آنمی و پلی‌سیتمی',
      subtitle: 'ارزیابی، طبقه‌بندی و اریتروسیتوز',
      links: [
        { title: 'درس 1: آنمی و پلی سیتمی', href: 'pages/01.html' }
      ]
    },
    {
      title: 'فصل ۲: آنمی فقر آهن و آنمی‌های هیپوپرولیفراتیو',
      subtitle: 'متابولیسم آهن و درمان',
      links: [{ title: 'درس 2: آنمی فقر آهن', href: 'pages/02.html' }]
    },
    {
      title: 'فصل ۳: آنمی‌های همولیتیک و خونریزی‌های حاد',
      subtitle: 'ویژگی‌ها و اختلالات همولیتیک',
      links: [{ title: 'درس 3: آنمی‌های همولیتیک', href: 'pages/03.html' }]
    },
    {
      title: 'فصل ۴: هموگلوبینوپاتی‌ها و اختلالات زنجیره گلوبین',
      subtitle: 'سیکل‌سل و تالاسمی',
      links: [{ title: 'درس 4: اختلالات هموگلوبین', href: 'pages/04.html' }]
    },
    {
      title: 'فصل ۵: آنمی آپلاستیک و نارسایی مغز استخوان',
      subtitle: 'آپلازی و MDS',
      links: [{ title: 'درس 5: آنمی آپالستیک و میلودیسپالزی', href: 'pages/05.html' }]
    },
    {
      title: 'فصل ۶: آنمی‌های مگالوبلاستیک',
      subtitle: 'کمبود B12 و فولات',
      links: [{ title: 'درس 6: آنمی مگالوبالستیک', href: 'pages/06.html' }]
    },
    {
      title: 'فصل ۷: طب انتقال خون',
      subtitle: 'فرآورده‌ها و عوارض',
      links: [{ title: 'درس 7: انتقال خون', href: 'pages/07.html' }]
    },
    {
      title: 'فصل ۸ و ۹: لوسمی‌های میلوئیدی (AML & CML)',
      subtitle: 'AML و CML',
      links: [{ title: 'درس 8: AML', href: 'pages/08.html' }, { title: 'درس 9: CML', href: 'pages/09.html' }]
    },
    {
      title: 'فصل ۱۰: اختلالات لنفوپرولیفراتیو و دیسکرازی‌های پلاسماسل',
      subtitle: 'لنفوم‌ها و میلوم',
      links: [{ title: 'درس 10: اختلالات لنفوسیت', href: 'pages/10.html' }]
    },
    {
      title: 'فصل ۱۲ و ۱۳: هموستاز، اختلالات انعقادی و ترومبوز',
      subtitle: 'هموستاز و ترومبوز',
      links: [{ title: 'درس 12: بیماری های هموستاتیک', href: 'pages/12.html' }, { title: 'درس 13: اختلالات ترومبوتیک', href: 'pages/13.html' }]
    },
    {
      title: 'بخش اُنکولوژی تخصصی',
      subtitle: 'بیولوژی و اپیدمیولوژی سرطان',
      links: [{ title: 'درس 14: اُنکولوژی', href: 'pages/14.html' }]
    }
  ];

  function renderSidebar() {
    const container = document.getElementById('global-sidebar');
    if (!container) return;
    const root = document.createElement('div');
    root.className = 'sidebar-root no-scrollbar';
    root.id = 'site-sidebar';

    const header = document.createElement('div');
    header.className = 'sidebar-header';
    header.innerHTML = `<div class="sidebar-title">نقشه درس</div><div style="font-size:.85rem;color:#64748b">فصل‌بندی</div>`;
    root.appendChild(header);

    const tree = document.createElement('div');
    tree.className = 'sidebar-tree';

    chapters.forEach((ch, idx) => {
      const box = document.createElement('div');
      box.className = 'chapter-box';
      box.innerHTML = `<div class="chapter-toggle" data-idx="${idx}"><div><div style="font-weight:800">${ch.title}</div><div style="font-size:.85rem;color:#475569">${ch.subtitle}</div></div><div style="opacity:.7">›</div></div>`;
      const children = document.createElement('div');
      children.className = 'chapter-children';
      ch.links.forEach(l => {
        const a = document.createElement('a');
        a.className = 'chapter-link';
        a.href = l.href;
        a.textContent = l.title;
        children.appendChild(a);
      });
      box.appendChild(children);
      tree.appendChild(box);
    });

    root.appendChild(tree);
    container.innerHTML = '';
    container.appendChild(root);

    // interactions
    root.querySelectorAll('.chapter-toggle').forEach(t=>{
      t.addEventListener('click', e=>{
        const p = t.parentElement;
        const ch = p.querySelector('.chapter-children');
        ch.classList.toggle('open');
      });
    });

    // highlight current link
    const current = document.body.getAttribute('data-page');
    if (current) {
      root.querySelectorAll('a.chapter-link').forEach(a=>{
        if (a.getAttribute('href').endsWith(current) || a.getAttribute('href').endsWith('/'+current)){
          a.classList.add('active');
          const parent = a.closest('.chapter-children');
          if (parent) parent.classList.add('open');
        }
      });
    }
  }

  // toggle button
  function wireToggle() {
    const toggle = document.getElementById('sidebarToggle');
    const container = document.getElementById('global-sidebar');
    if (!toggle || !container) return;
    toggle.addEventListener('click', ()=>{
      const root = document.getElementById('site-sidebar');
      if (!root) return;
      root.classList.toggle('open');
    });
  }

  // existing scrollspy logic (sections) preserved where present
  const sectionLinks = document.querySelectorAll('a[data-section]');
  const sections = Array.from(sectionLinks)
    .map(a => document.getElementById(a.getAttribute('href').slice(1)))
    .filter(Boolean);
  const onScroll = () => {
    const y = window.scrollY + 140;
    let activeId = null;
    for (const s of sections) {
      if (s.offsetTop <= y) activeId = s.id;
    }
    if (!activeId) return;
    sectionLinks.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + activeId);
    });
  };
  if (sections.length) {
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // init
  document.addEventListener('DOMContentLoaded', ()=>{
    renderSidebar();
    wireToggle();
    // set page title element if present (use document.title before '|')
    const el = document.getElementById('page-title');
    if (el) {
      const t = (document.title || '').split('|')[0].trim();
      el.textContent = t || '';
    }
  });
})();
