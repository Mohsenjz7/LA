from pathlib import Path
import html,json
from bs4 import BeautifulSoup

TITLES={'exercises':'تمرین‌های تئوری','nhw2':'تمرین تئوری دوم (NHW2) — ۱۰ سؤال','ht2':'حل تمرین تئوری دوم (HT2) — ۶ سؤال'}

def exercise_pages(root,render,fa):
    data=json.loads((root/'content/exercises.json').read_text(encoding='utf-8'))
    intro='در این بخش تمام سؤال\u200cهای دو برگه\u200cی تمرین استقلال خطی، بُعد، پایه و رتبه\u200cی ماتریس (پاییز ۱۴۰۵) قرار دارند. هر سؤال را ابتدا خودت حل کن؛ پاسخ فقط پس از کلیک روی دکمه\u200cی «نمایش پاسخ» زیر همان سؤال باز می\u200cشود.\n\nپاسخ\u200cهای NHW2 بر اساس پاسخ\u200cنامه\u200cی ارسالی بازنویسی شده\u200cاند و تصویر اصل پاسخ\u200cنامه در کنار هر جواب قرار دارد. پاسخ\u200cهای HT2 به\u200cصورت مستقل و تشریحی حل شده\u200cاند. فایل\u200cهای اصلی برای مراجعه بدون تغییر در پروژه موجودند.'
    links='<div class="exercise-overview"><a class="exercise-tile" href="nhw2.html"><span class="sheet-tag">NHW2</span><strong>تمرین تئوری دوم</strong><span>۱۰ سؤال · پاسخ\u200cنامه\u200cی ارسالی</span><span class="tile-arrow">شروع حل تمرین ←</span></a><a class="exercise-tile" href="ht2.html"><span class="sheet-tag">HT2</span><strong>حل تمرین تئوری دوم</strong><span>۶ سؤال · حل تشریحی مستقل</span><span class="tile-arrow">شروع حل تمرین ←</span></a></div><h2 id="pdfs">فایل\u200cهای اصلی تمرین\u200cها</h2><div class="source-list"><a href="../sources/LA_NHW2_Problems_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW2_Problems_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_NHW2_Solutions_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW2_Solutions_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_HT2_Fall2026.pdf" target="_blank" rel="noopener">LA_HT2_Fall2026.pdf <small>PDF ↗</small></a></div>'
    ih,_=render(intro)
    pages=[{'id':'exercises','chapter':'ex','kind':'exercise','title':TITLES['exercises'],'body':intro,'html':ih+links,'toc':[{'id':'pdfs','title':'فایل‌های اصلی تمرین‌ها'}],'plain':intro+' NHW2 HT2 تمرین تئوری'}]
    transcript=['# تمرین‌های تئوری\n\n'+intro]
    for sheet,questions in data.items():
        title=TITLES[sheet]; official=sheet=='nhw2'; count=len(questions)
        filename='LA_NHW2_Problems_Fall2026.pdf' if official else 'LA_HT2_Fall2026.pdf'
        intro2=('پاسخ‌ها بر اساس پاسخ‌نامه‌ی ارسالی بازنویسی شده‌اند؛ تصویر متن اصلی هر پاسخ نیز درون همان پاسخ موجود است.' if official else 'پاسخ‌ها حل تشریحی مستقل هستند و همه‌ی قسمت‌های سؤال‌ها را پوشش می‌دهند.')
        intro2+=' تمام جواب‌ها در ابتدا بسته‌اند.'
        out=[f'<p>{html.escape(intro2)}</p><div class="exercise-actions"><a class="secondary" href="../sources/{filename}" target="_blank" rel="noopener">صورت سؤال اصلی (PDF) ↗</a>'+ ('<a class="secondary" href="../sources/LA_NHW2_Solutions_Fall2026.pdf" target="_blank" rel="noopener">پاسخ‌نامه‌ی اصلی (PDF) ↗</a>' if official else '')+'</div>']
        out.append('<div class="exercise-jump" aria-label="رفتن به سؤال">'+''.join(f'<a href="#q-{i}">{fa(i)}</a>' for i in range(1,count+1))+'</div>')
        toc=[]; blocks=[f'# {title}\n\n{intro2}']
        for i,question in enumerate(questions,1):
            qhtml,_=render(question['question']); ahtml,_=render(question['answer'])
            # Avoid duplicate subheading IDs from separate renders. The visible TOC includes questions only.
            soup=BeautifulSoup(ahtml,'html.parser')
            for h in soup.find_all(['h2','h3','h4']):
                if h.has_attr('id'):h['id']=f'q-{i}-'+h['id']
            ahtml=str(soup)
            source=''
            if official:
                pagestr='، '.join(fa(p) for p in question['source_pages'])
                figs=''.join(f'<figure class="official-figure"><a href="../{im["path"]}" target="_blank" rel="noopener"><img src="../{im["path"]}" loading="lazy" alt="اصل پاسخ NHW2 سؤال {fa(i)}، صفحه {fa(im["page"])}"></a><figcaption>صفحه {fa(im["page"])} پاسخ‌نامه · برای بزرگ‌نمایی روی تصویر کلیک کن</figcaption></figure>' for im in question['official_images'])
                source=f'<p class="answer-source">منبع: پاسخ‌نامه‌ی NHW2، صفحه‌های {pagestr}. متن بالا بازنویسی آموزشی پاسخ است.</p><details class="official-original"><summary>مشاهده‌ی تصویر اصل پاسخ‌نامه</summary><div>{figs}</div></details>'
            else:source='<p class="answer-source">حل تشریحی مستقل بر اساس صورت سؤال HT2.</p>'
            heading=f'پرسش {fa(i)} — {question["title"]}'
            out.append(f'<section class="exercise-question" id="q-{i}"><div class="question-kicker"><span>{sheet.upper()} / {fa(i)}</span><span>۰ نمره · غیرتحویلی</span></div><h2>{html.escape(heading)}</h2><div class="question-body">{qhtml}</div><details class="exercise-answer" id="answer-{i}"><summary><span class="answer-label"><span class="closed-label">نمایش پاسخ تشریحی</span><span class="open-label">پنهان کردن پاسخ</span></span><span class="answer-chevron" aria-hidden="true">⌄</span></summary><div class="answer-body">{ahtml}{source}</div></details></section>')
            toc.append({'id':f'q-{i}','title':heading})
            blocks.append(f'## {heading}\n\n{question["question"]}\n\n### پاسخ تشریحی\n\n{question["answer"]}\n\n'+ ('منبع: پاسخ‌نامه NHW2، صفحات '+', '.join(map(str,question['source_pages'])) if official else 'حل مستقل HT2'))
        body='\n\n'.join(blocks)
        plain=BeautifulSoup(''.join(out),'html.parser').get_text(' ',strip=True)
        pages.append({'id':sheet,'chapter':'ex','kind':'exercise','title':title,'body':body,'html':''.join(out),'toc':toc,'plain':plain})
        transcript.append(body)
    return pages,'\n\n---\n\n'.join(transcript)
