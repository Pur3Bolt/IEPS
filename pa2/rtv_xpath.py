import json
from lxml import html


f = open("strani/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r", encoding='utf-8')
s = f.read()
tree = html.fromstring(s)

author = "//div[@class='author-name']/text()"
published_time = "//div[@class='publish-meta']/text()"
title = '//h1/text()'
subtitle = "//div[@class='subtitle']/text()"
lead = "//p[@class='lead']/text()"
content = "//div[@class='article-body']/descendant-or-self::*/text()"

xp_author = tree.xpath(author)
xp_published_time = tree.xpath(published_time)
xp_title = tree.xpath(title)
xp_subtitle = tree.xpath(subtitle)
xp_lead = tree.xpath(lead)
xp_content = tree.xpath(content)

items = {
    'Author': xp_author[0],
    'PublishedTime': xp_published_time[0].strip(),
    'Title': xp_title[0],
    'SubTitle': xp_subtitle[0],
    'Lead': xp_lead[0],
    'Content': " ".join(xp_content)
}
print(items)
