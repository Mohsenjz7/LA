"""New chapters 8-9: keep the user-supplied Markdown bytes intact on disk.
Only escape/normalization needed for web display is applied in memory.
"""
from pathlib import Path
import re,html
from bs4 import BeautifulSoup

SLIDE_MAP={
 '08-01':[(10,'مثال میانگین و بیشینه در اسلاید ۱۰','مثال اسلاید')],
 '08-02':[(18,'نمونهٔ تغییر پایهٔ فرم دوخطی در اسلاید ۱۸','مثال خود اسلاید ۱۸')],
 '08-03':[(20,'تعریف فرم دوخطی در فضای مختلط، اسلاید ۲۰','خطی و مزدوج')],
 '08-04':[(26,'تعریف ضرب داخلی در اسلاید ۲۶','تعریف ضرب داخلی'),(28,'ضرب داخلی ماتریسی، اسلاید ۲۸','ضرب داخلی ماتریس'),(29,'ضرب داخلی توابع، اسلاید ۲۹','ضرب داخلی توابع')],
 '08-05':[(35,'نسبت ضرب داخلی، نرم و فاصله در اسلاید ۳۵','مثال اضافهٔ ۱')],
 '08-06':[(38,'ویژگی‌های نرم برداری، اسلاید ۳۸','تعریف نرم'),(39,'رابطهٔ نرم و ضرب داخلی، اسلاید ۳۹','ارتباط ضرب داخلی و نرم'),(45,'نرم جمع دو بردار، اسلاید ۴۵','نامساوی مثلثی'),(47,'نمایش هندسی فاصله، اسلاید ۴۷','Metric')],
 '09-01':[(5,'نمایش هندسی بردارهای متعامد، اسلاید ۵','تعامد دو بردار'),(4,'تعریف مجموعهٔ متعامد یکه، اسلاید ۴','مجموعهٔ متعامد و متعامد یکه'),(9,'مثال ضرایب نسبت به بردارهای متعامد، اسلاید ۹','مثال خود اسلاید ۹')],
 '09-02':[(11,'تعریف و مثال زیرفضاهای متعامد، اسلاید ۱۱','تعریف')],
 '09-03':[(13,'نمایش هندسی متمم متعامد، اسلاید ۱۳','تعریف'),(14,'قضایای متمم متعامد، اسلاید ۱۴','قضایای مهم')],
 '09-04':[(16,'تصویر هندسی فرایند گرام–اشمیت، اسلاید ۱۶','ایدهٔ اصلی'),(18,'مثال گرام–اشمیت، اسلاید ۱۸','مثال خود اسلاید ۱۸'),(21,'پیچیدگی گرام–اشمیت، اسلاید ۲۱','پیچیدگی زمانی')],
 '09-05':[(25,'نمودار چهار زیرفضای بنیادی، اسلاید ۲۵','رابطه‌های اصلی')]
}


def web_math(raw):
    # Pasted input has double-escaped MathJax delimiters, while commands inside
    # the formula have single escapes. Fix presentation, not the actual source.
    for a,b in [(r'\\[',r'\['),(r'\\]',r'\]'),(r'\\(',r'\('),(r'\\)',r'\)')]:
        raw=raw.replace(a,b)
    # TeX indices were escaped during copy-paste into Markdown.
    raw=raw.replace(r'\_', '_')
    # Copy-paste also doubled the TeX delimiters for literal braces and norms.
    for c in ('{','}','|'):
        raw=raw.replace('\\\\'+c, '\\'+c)
    return raw


def add_slide_figures(rendered,slug):
    if slug not in SLIDE_MAP: return rendered
    soup=BeautifulSoup(rendered,'html.parser')
    for slide,caption,needle in SLIDE_MAP[slug]:
        chapter=slug[:2];file=f'../assets/slides/{chapter}-slide-{slide:02}.webp'
        pdf='8-Inner%20Product%20Space.pdf' if chapter=='08' else '9-Orthogonality.pdf'
        fig=soup.new_tag('figure',attrs={'class':'lecture-slide'})
        a=soup.new_tag('a',href=file,target='_blank',rel='noopener',attrs={'aria-label':f'بزرگ‌نمایی اسلاید {slide}'})
        img=soup.new_tag('img',src=file,loading='lazy',alt=caption)
        a.append(img);fig.append(a)
        tag=soup.new_tag('figcaption')
        tag.append(caption+' · ')
        src=soup.new_tag('a',href=f'../sources/{pdf}#page={slide}',target='_blank',rel='noopener')
        src.string='دیدن در PDF اصلی'
        tag.append(src);fig.append(tag)
        headers=soup.find_all(['h2','h3','h4'])
        target=next((h for h in headers if needle in h.get_text(' ',strip=True)),None)
        if target:target.insert_after(fig)
        elif headers: headers[0].insert_after(fig)
        else:soup.append(fig)
    return str(soup)


def new_lesson_pages(root,render,fa):
    text=(root/'content/08-09-original.md').read_text(encoding='utf-8')
    chapter_heads=list(re.finditer(r'(?m)^# \*\*فصل ([۸۹])\s*—[^\n]*$',text))
    assert len(chapter_heads)==2, 'Missing input chapter headings'
    result=[]
    for ci,ch in enumerate(chapter_heads):
        code='08' if ch.group(1)=='۸' else '09'
        end=chapter_heads[ci+1].start() if ci+1<len(chapter_heads) else len(text)
        source=text[ch.start():end]
        starts=list(re.finditer(r'(?m)^## \*\*بخش ([۱-۹]):[^\n]*$',source))
        assert len(starts)==6,(code,len(starts))
        prefix=(text[:ch.start()] if ci==0 else "")+source[:starts[0].start()]
        for i,m in enumerate(starts):
            fromidx=m.start();toidx=starts[i+1].start() if i<len(starts)-1 else len(source)
            raw=(prefix if i==0 else '')+source[fromidx:toidx]
            # The final review follows chapter 9 section 6 verbatim.
            title=m.group().replace('## **','').replace('**','')
            slug=f'{code}-{i+1:02}'
            result.append({'id':slug,'chapter':code,'kind':'lesson','title':title,
                'body':raw,'render_body':web_math(raw),'slide_images':True})
    return result
