import re


f = open("input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r", encoding='utf-8')
s = f.read()
author = '<div class="author-name">(.+?)</div>'
published_time = '<div class="publish-meta">[\n\t]*(.+?)<br>'
title = '<h1>(.+?)</h1>'
subtitle = '<div class="subtitle">(.+?)</div>'
lead = '<p class="lead">(.+?)</p>'
content = '<article class="article">.*?</figure>(.+?)</article>'
re_author = re.findall(author, s)
re_published_time = re.findall(published_time, s)
re_title = re.findall(title, s)
re_subtitle = re.findall(subtitle, s)
re_lead = re.findall(lead, s)
re_content = re.findall(content, s, re.DOTALL)
re_content = re.sub('<iframe[^>]*>.*?</iframe>', '', re_content[0])
re_content = re.sub('<figure[^>]*>.*?</figure>', '', re_content, flags=re.DOTALL)
re_content = re.sub('<div class="gallery">.*</div>', '', re_content, flags=re.DOTALL)
re_content = re.sub('<p[^>]*>', '', re_content)
re_content = re.sub('</p>', '\n', re_content)
re_content = re.sub('<strong>', '', re_content)
re_content = re.sub('</strong>', '', re_content)
re_content = re.sub('<br>', '\n', re_content)
re_content = re.sub('<sub>', '', re_content)
re_content = re.sub('</sub>', '', re_content)
items = {
    'Author': re_author[0],
    'PublishedTime': re_published_time[0],
    'Title': re_title[0],
    'SubTitle': re_subtitle[0],
    'Lead': re_lead[0],
    'Content': re_content.strip()
}
print(items)
