import json
from lxml import html


f = open("strani/overstock.com/jewelry01.html", "r")
s = f.read()
tree = html.fromstring(s)

title = '//td[@valign="top"]/a/b/text()'
listprice = '//td[@align="left"][@nowrap]/s/text()'
price = '//span[@class="bigred"]/b/text()'
saving = '//span[@class="littleorange"]/text()'
content = '//span[@class="normal"]/descendant-or-self::*/text()'

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
        'Content': xp_content[2*i]+' '+xp_content[2*i+1],
    }
print(json.dumps(items, indent=4))
# print(items)
