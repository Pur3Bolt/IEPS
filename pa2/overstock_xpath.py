import json
from lxml import html


f = open("strani/overstock.com/jewelry01.html", "r")
s = f.read()
tree = html.fromstring(s)
title = '//tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/a/b/text()'
listprice = '//td[2]/s/text()'
price = '//tr[2]/td[2]/span/b/text()'
saving = "//tr[3]/td[2]/span/text()"
content = '//td[2]/table/tbody/tr/td[2]/span/text()'
xp_title = tree.xpath(title)
xp_listprice = tree.xpath(listprice)
xp_price = tree.xpath(price)
xp_saving = tree.xpath(saving)
xp_content = tree.xpath(content)

items = {}
for i in range(len(xp_title)):
    items[i+1] = {
        'Title': xp_title[i],
        'ListPrice': xp_listprice[i],
        'Price': xp_price[i],
        'Saving': xp_saving[i][:xp_saving[i].index(' (')],
        'SavingPercent': xp_saving[i][xp_saving[i].index('(')+1:-1],
        'Content': xp_content[i],
    }
print(json.dumps(items, indent=4))
