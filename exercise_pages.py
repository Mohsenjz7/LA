from pathlib import Path
import html,json
from bs4 import BeautifulSoup

TITLES={'exercises':'تمرین‌های تئوری','nhw2':'تمرین تئوری دوم (NHW2) — ۱۰ سؤال','ht2':'حل تمرین تئوری دوم (HT2) — ۶ سؤال','nhw3':'تمرین تئوری سوم (NHW3) — ۸ سؤال'}

def exercise_pages(root,render,fa):
    data=json.loads((root/'content/exercises.json').read_text(encoding='utf-8'))
    intro='در این بخش تمام سؤال\u200cهای تمرین دوم و سوم درس جبر خطی (پاییز ۱۴۰۵) قرار دارند. هر سؤال را ابتدا خودت حل کن؛ پاسخ فقط پس از کلیک روی دکمه\u200cی «نمایش پاسخ» زیر همان سؤال باز می\u200cشود.\n\nپاسخ\u200cهای NHW2 بر اساس پاسخ\u200cنامه\u200cی ارسالی بازنویسی شده\u200cاند و تصویر اصل پاسخ\u200cنامه در کنار هر جواب قرار دارد. پاسخ\u200cهای HT2 به\u200cصورت مستقل و تشریحی حل شده\u200cاند. فایل\u200cهای اصلی برای مراجعه بدون تغییر در پروژه موجودند. تمرین سوم شامل فضاهای ضرب داخلی و تعامد است.'
    links='<div class="exercise-overview"><a class="exercise-tile" href="nhw2.html"><span class="sheet-tag">NHW2 · تمرین ۲</span><strong>تمرین تئوری دوم</strong><span>۱۰ سؤال · پاسخ\u200cنامه\u200cی ارسالی</span><span class="tile-arrow">شروع حل تمرین ←</span></a><a class="exercise-tile" href="ht2.html"><span class="sheet-tag">HT2 · تمرین ۲</span><strong>حل تمرین تئوری دوم</strong><span>۶ سؤال · حل تشریحی مستقل</span><span class="tile-arrow">شروع حل تمرین ←</span></a><a class="exercise-tile" href="nhw3.html"><span class="sheet-tag">NHW3 · تمرین ۳</span><strong>تمرین تئوری سوم</strong><span>۸ سؤال · پاسخ‌نامهٔ ارسالی و تصاویر اصل سؤال‌ها</span><span class="tile-arrow">مشاهدهٔ تمرین سوم ←</span></a></div><h2 id="pdfs">فایل\u200cهای اصلی تمرین\u200cها</h2><div class="source-list"><a href="../sources/LA_NHW2_Problems_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW2_Problems_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_NHW2_Solutions_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW2_Solutions_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_HT2_Fall2026.pdf" target="_blank" rel="noopener">LA_HT2_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_NHW3_Problems_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW3_Problems_Fall2026.pdf <small>PDF ↗</small></a><a href="../sources/LA_NHW3_Solutions_Fall2026.pdf" target="_blank" rel="noopener">LA_NHW3_Solutions_Fall2026.pdf <small>PDF ↗</small></a></div>'
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
    # The third assignment has the full official questions and solutions as crops,
    # in addition to legible searchable text and the untouched PDFs.
    nh3=json.loads((root/'content/nhw3.json').read_text(encoding='utf-8'))
    nh3title=TITLES['nhw3']
    intro3='هشت پرسش تمرین تئوری سوم دربارهٔ فضای ضرب داخلی، تعامد، متمم متعامد، گرام–اشمیت و کوشی–شوارتز. صورت سؤال و پاسخ تشریحی قابل مطالعه است؛ تصویر برگهٔ اصلی نیز برای حفظ متن ارسالی کنار هر بخش قرار دارد. برای دیدن جواب، «نمایش پاسخ تشریحی» را باز کن.'
    out3=[f'<p>{html.escape(intro3)}</p><div class="exercise-actions"><a class="secondary" href="../sources/LA_NHW3_Problems_Fall2026.pdf" target="_blank" rel="noopener">صورت سؤال‌های اصلی (PDF) ↗</a><a class="secondary" href="../sources/LA_NHW3_Solutions_Fall2026.pdf" target="_blank" rel="noopener">پاسخ‌نامهٔ اصلی (PDF) ↗</a></div>']
    out3.append('<div class="exercise-jump" aria-label="رفتن به سؤال">'+''.join(f'<a href="#q-{i}">{fa(i)}</a>' for i in range(1,len(nh3)+1))+'</div>')
    toc3=[];rawblocks=[f'# {nh3title}\n\n{intro3}']
    for i,q in enumerate(nh3,1):
        qhtml,_=render(q['question']); ahtml,_=render(q['answer'])
        qs=f'../assets/official-answers/nhw3-{i:02}-question.webp'
        ans=f'../assets/official-answers/nhw3-{i:02}-solution.webp'
        image_question=f'<figure class="official-figure official-question"><a href="{qs}" target="_blank" rel="noopener"><img src="{qs}" loading="lazy" alt="تصویر متن دقیق سؤال {fa(i)} از برگهٔ رسمی تمرین سوم"></a><figcaption>تصویر صورت سؤال {fa(i)} از PDF ارسالی · برای بزرگ‌نمایی کلیک کن</figcaption></figure>'
        image_answer=f'<figure class="official-figure"><a href="{ans}" target="_blank" rel="noopener"><img src="{ans}" loading="lazy" alt="تصویر پاسخ رسمی سؤال {fa(i)} تمرین سوم"></a><figcaption>پاسخ رسمی سؤال {fa(i)}، بدون تغییر · برای بزرگ‌نمایی کلیک کن</figcaption></figure>'
        title=f'پرسش {fa(i)} — {q["title"]}'
        out3.append(f'<section class="exercise-question" id="q-{i}"><div class="question-kicker"><span>NHW3 / {fa(i)}</span><span>۰ نمره · غیرتحویلی</span></div><h2>{html.escape(title)}</h2><div class="question-body">{qhtml}{image_question}</div><details class="exercise-answer" id="answer-{i}"><summary><span class="answer-label"><span class="closed-label">نمایش پاسخ تشریحی</span><span class="open-label">پنهان کردن پاسخ</span></span><span class="answer-chevron" aria-hidden="true">⌄</span></summary><div class="answer-body">{ahtml}<p class="answer-source">پاسخ طبق پاسخ‌نامهٔ ارسالی؛ تصویر اصل پاسخ در زیر آمده است.</p>{image_answer}</div></details></section>')
        toc3.append({'id':f'q-{i}','title':title})
        rawblocks.append(f'## {title}\n\n{q["question"]}\n\n### پاسخ تشریحی\n\n{q["answer"]}\n\n[تصویر اصل سؤال و پاسخ در وب و فایل‌های PDF رسمی موجود است.]')
    page3={'id':'nhw3','chapter':'ex','kind':'exercise','title':nh3title,'body':'\n\n'.join(rawblocks),'html':''.join(out3),'toc':toc3,'plain':BeautifulSoup(''.join(out3),'html.parser').get_text(' ',strip=True)}
    pages.append(page3)
    transcript.append(page3['body'])
    return pages,'\n\n---\n\n'.join(transcript)
