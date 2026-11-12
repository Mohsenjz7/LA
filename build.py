from pathlib import Path
import re, json, html
import mistune
from exercise_pages import exercise_pages, TITLES as EX_TITLES
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
WIDGET_TEXT=json.loads((ROOT/'content/widget-text.json').read_text(encoding='utf-8'))
WIDGET_RE=r'<!--widget:([\w-]+)-->'
def expand_widgets(text):
    return re.sub(WIDGET_RE,lambda m: '\n\n'+WIDGET_TEXT[m.group(1)]+'\n\n',text)
md=mistune.create_markdown(escape=False,plugins=['table'])
chapters={'05':'استقلال خطی','06':'پایه و بُعد','07':'رتبه ماتریس'}
FA='۰۱۲۳۴۵۶۷۸۹'; EN='0123456789'
def fa(n):return str(n).translate(str.maketrans(EN,FA))
def render(text):
    math=[]
    def protect(m):
        math.append(m.group());return f'ZZMATH{len(math)-1}ZZ'
    text=re.sub(r'\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)',protect,text)
    text=re.sub(r'<!--widget:([\w-]+)-->',r'<div class="widget" data-widget="\1"></div>',text)
    result=md(text)
    def restore(m):
        expr=math[int(m.group(1))];safe=html.escape(expr,quote=False)
        return '<span class="math-display" dir="ltr">'+safe+'</span>' if expr.startswith(r'\[') else '<span class="math-inline" dir="ltr">'+safe+'</span>'
    result=re.sub(r'ZZMATH(\d+)ZZ',restore,result)
    soup=BeautifulSoup(result,'html.parser')
    toc=[]
    for i,h in enumerate(soup.find_all(['h2','h3','h4'])):
        h['id']=f'sub-{i+1}'; toc.append({'id':h['id'],'title':h.get_text(' ',strip=True)})
    for table in soup.find_all('table'):
        wrapper=soup.new_tag('div',attrs={'class':'table-scroll'});table.wrap(wrapper)
    return str(soup),toc
pages=[]
intro=(ROOT/'content/00.md').read_text(); title, body=intro.split('\n',1)
pages.append({'id':'index','chapter':'00','title':title[2:],'body':body,'kind':'home'})
for ch in chapters:
    src=(ROOT/f'content/{ch}.md').read_text(); first, rest=src.split('\n',1)
    parts=re.split(r'(?m)^## (?=بخش |جمع‌بندی فصل|آزمون نهایی|خلاصه‌ی نهایی|چند اصلاح علمی)',rest)
    pref=parts[0].strip();count=0
    for part in parts[1:]:
        heading, sep,body=part.partition('\n');heading=heading.strip()
        if heading.startswith('بخش '):
            count+=1;slug=f'{ch}-{count:02}';kind='lesson'
            if count==1:body='### '+first[2:]+'\n\n'+(pref+'\n\n' if pref else '')+body
        elif heading.startswith('جمع‌بندی'):slug=f'{ch}-review';kind='review'
        elif heading.startswith('آزمون'):slug='final-quiz';kind='quiz'
        elif heading.startswith('خلاصه'):slug='formula-sheet';kind='review'
        else:slug='corrections';kind='review'
        pages.append({'id':slug,'chapter':ch,'title':heading,'body':body,'kind':kind,'chapter_title':first[2:]})
    assert count=={'05':11,'06':12,'07':17}[ch], (ch,count)

exercise_data,exercise_transcript=exercise_pages(ROOT,render,fa)
pages.extend(exercise_data)

def url(p,base): return base+'index.html' if p['id']=='index' else base+'pages/'+p['id']+'.html'
for p in pages:
    if p['kind']=='exercise':continue
    p['html'],p['toc']=render(p['body'])
    p['plain']=BeautifulSoup(p['html'],'html.parser').get_text(' ',strip=True)
    p['plain']+=' '+ ' '.join(WIDGET_TEXT[k] for k in re.findall(WIDGET_RE,p['body']))

for i,p in enumerate(pages):
    base='./' if p['id']=='index' else '../'; chapter=p['chapter']; title=p['title']; esc=html.escape
    def link(q, cls=''):
        active=' active' if p['id']==q['id'] else ''
        return f'<a class="nav-link {cls}{active}" href="{url(q,base)}" '+('aria-current="page"' if active else '')+f' data-page="{q["id"]}"><span>{esc(q["title"])}</span><span class="done-dot" aria-hidden="true"></span></a>'
    nav=link(pages[0])
    for ch,name in chapters.items():
        nav+=f'<details class="chapter" {"open" if chapter==ch or chapter=="00" else ""}><summary><span class="chapter-number">{fa(int(ch))}</span><span>{name}</span><span class="chevron">⌄</span></summary><div class="chapter-links">'+''.join(link(q) for q in pages if q['chapter']==ch and q['id'] not in ['final-quiz','formula-sheet','corrections'])+'</div></details>'
    nav+='<div class="nav-label">مرور نهایی</div>'+''.join(link(q) for q in pages if q['id'] in ['final-quiz','formula-sheet','corrections'])
    nav+='<details class="chapter exercise-nav" '+('open' if chapter=='ex' or chapter=='00' else '')+'><summary><span class="chapter-number">✎</span><span>تمرین‌های تئوری</span><span class="chevron">⌄</span></summary><div class="chapter-links">'+''.join(link(q) for q in pages if q['chapter']=='ex')+'</div></details>'
    toc=''.join(f'<a href="#{t["id"]}">{esc(t["title"])}</a>' for t in p['toc'])
    pager=''
    if i>0:pager+=f'<a class="page-link" href="{url(pages[i-1],base)}"><small>← بخش قبلی</small><span>{esc(pages[i-1]["title"])}</span></a>'
    else:pager+='<span></span>'
    if i<len(pages)-1:pager+=f'<a class="page-link next" href="{url(pages[i+1],base)}"><small>بخش بعدی →</small><span>{esc(pages[i+1]["title"])}</span></a>'
    home=''
    if p['id']=='index':
        home='<div class="course-cards">'+''.join(f'<a class="course-card" href="{base}pages/{ch}-01.html"><span class="course-number">{fa(int(ch))}</span><strong>{name}</strong><span>{fa(sum(1 for q in pages if q["chapter"]==ch and q["kind"]=="lesson"))} بخش آموزشی</span><span class="card-arrow">شروع فصل ←</span></a>' for ch,name in chapters.items())+'</div><h2>فایل‌های اصلی جزوه</h2><div class="source-list">'+''.join(f'<a href="{base}sources/{f.name.replace(" ","%20")}" target="_blank" rel="noopener">{esc(f.name)} <small>PDF ↗</small></a>' for f in sorted((ROOT/'sources').glob('*.pdf')))+'</div>'
    if p['id']=='index':home=f'<h2>تمرین‌های تئوری</h2><div class="exercise-overview"><a class="exercise-tile" href="{base}pages/nhw2.html"><span class="sheet-tag">NHW2</span><strong>تمرین تئوری دوم</strong><span>۱۰ سؤال · پاسخ‌نامه‌ی ارسالی</span><span class="tile-arrow">شروع حل تمرین ←</span></a><a class="exercise-tile" href="{base}pages/ht2.html"><span class="sheet-tag">HT2</span><strong>حل تمرین تئوری دوم</strong><span>۶ سؤال · حل تشریحی مستقل</span><span class="tile-arrow">شروع حل تمرین ←</span></a></div>'+home
    if p['id']=='index':home+=f'<h2>متن یکپارچه‌ی همه‌ی مطالب</h2><p><a href="{base}content/full-transcript.md" download>دریافت متن کامل آموزش، فرمول‌ها، آزمون‌ها و متن نمودارها (Markdown)</a></p>'
    content=f'''<!doctype html><html lang="fa" dir="rtl" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | جبر خطی</title><link rel="stylesheet" href="{base}assets/style.css"><script>try{{document.documentElement.dataset.theme=localStorage.getItem('la-theme')||'light'}}catch(e){{}}</script><script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']],processEscapes:true}},svg:{{fontCache:'local'}},options:{{skipHtmlTags:['script','noscript','style','textarea','pre','code']}}}};</script><script defer src="{base}assets/mathjax/tex-svg.js"></script><script defer src="{base}assets/search-data.js"></script><script defer src="{base}assets/widgets.js"></script><script defer src="{base}assets/app.js"></script></head><body data-page="{p['id']}" data-base="{base}"><a class="skip" href="#lesson">رفتن به متن درس</a><header class="topbar"><div class="brand"><button class="icon-btn" id="menu-toggle" aria-label="فهرست فصل‌ها" aria-expanded="false">☰</button><a href="{base}index.html" class="brand-link"><span class="logo">∑</span><span><strong>جبر خطی</strong><small>Linear Algebra · CE282</small></span></a></div><div class="toolbar"><button id="search-open" class="search-button" type="button">⌕ <span>جستجو در درس‌ها</span><kbd>Ctrl K</kbd></button><button class="icon-btn" id="theme-toggle" aria-label="تغییر پوسته">☾</button></div></header><div class="layout"><aside class="sidebar" id="sidebar"><div class="progress-title">پیشرفت مطالعه <span id="progress-count">۰ / ۴۰</span></div><div class="progress-track"><div id="progress-fill"></div></div><nav aria-label="فهرست درس‌ها">{nav}</nav></aside><main id="lesson"><div class="breadcrumb"><a href="{base}index.html">خانه</a><span> / </span><span>{esc(chapters.get(chapter,'تمرین‌های تئوری' if chapter=='ex' else 'آغاز دوره'))}</span></div><div class="lesson-header"><div class="eyebrow">{'آموزش جامع · سه فصل' if p['id']=='index' else 'تمرین‌های تئوری · پاییز ۱۴۰۵' if chapter=='ex' else 'فصل '+fa(int(chapter))+' · '+('درس' if p['kind']=='lesson' else 'مرور و تمرین')}</div><h1>{esc(title)}</h1><div class="meta">{'۴۰ بخش آموزشی · مطالعه مرحله‌به‌مرحله' if p['id']=='index' else f'صفحه {fa(i)} از {fa(len(pages)-1)} · '+fa(max(1,round(len(p["plain"].split())/140)))+' دقیقه مطالعه تقریبی'}</div></div><article class="article">{p['html']}{home}</article>{'<button class="complete" id="complete-btn">✓ علامت‌گذاری به عنوان مطالعه‌شده</button>' if p['kind']=='lesson' else ''}<nav class="pager" aria-label="بخش قبلی و بعدی">{pager}</nav><footer>جزوه‌ی آموزشی جبر خطی · نسخه محلی · فایل‌های اصلی در صفحه خانه</footer></main><aside class="toc" aria-label="در این صفحه">{('<h2>در این صفحه</h2>'+toc) if toc else ''}</aside></div><dialog id="search-dialog"><div class="dialog-head"><strong>جستجو در محتوای تمام فصل‌ها</strong><button id="search-close" class="icon-btn" aria-label="بستن">×</button></div><input id="search-input" type="search" placeholder="مثلاً فضای پوچ، Pivot، پایه..." autocomplete="off"><div id="search-results" aria-live="polite"></div></dialog></body></html>'''
    # math in headings needs render as math, not escaped markup
    dest=ROOT/'index.html' if p['id']=='index' else ROOT/'pages'/f'{p["id"]}.html'
    dest.write_text(content,encoding='utf-8')
search=[{'id':p['id'],'title':p['title'],'chapter':chapters.get(p['chapter'],'تمرین‌های تئوری' if p['chapter']=='ex' else 'مقدمه'),'text':p['plain'],'kind':p['kind']} for p in pages]
(ROOT/'assets/search-data.js').write_text('window.COURSE_PAGES='+json.dumps(search,ensure_ascii=False)+';',encoding='utf-8')
(ROOT/'content/full-transcript.md').write_text(expand_widgets('\n\n---\n\n'.join((ROOT/f'content/{ch}.md').read_text() for ch in ['00','05','06','07']))+'\n\n---\n\n'+exercise_transcript,encoding='utf-8')
print('Built',len(pages),'pages;',sum(p['kind']=='lesson' for p in pages),'numbered lessons')
