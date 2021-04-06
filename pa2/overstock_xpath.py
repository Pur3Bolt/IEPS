import json
from lxml import html
import elementpath


f = open("input-extraction/overstock.com/jewelry01.html", "r")
s = f.read()
tree = html.fromstring(s)

title = '//td[@valign="top"]/a/b/text()'
listprice = '//td[@align="left"][@nowrap]/s/text()'
price = '//span[@class="bigred"]/b/text()'
saving = '//td[@align="left"]/span[@class="littleorange"]/substring-before(text(), " (")'
saving_percent = '//td[@align="left"]/span[@class="littleorange"]/substring-before(substring-after(text(), " ("), ")")'
content = '//span[@class="normal"]/descendant-or-self::*/text()'

xp_title = tree.xpath(title)
xp_listprice = tree.xpath(listprice)
xp_price = tree.xpath(price)
xp_saving = elementpath.select(tree, saving)
xp_saving_percent = elementpath.select(tree, saving_percent)
xp_content = tree.xpath(content)

items = {}
for i in range(len(xp_title)):
    items[i+1] = {
        'Title': xp_title[i],
        'ListPrice': xp_listprice[i],
        'Price': xp_price[i],
        'Saving': xp_saving[i],
        'SavingPercent': xp_saving_percent[i],
        'Content': xp_content[2*i]+' '+xp_content[2*i+1],
    }
# print(json.dumps(items, indent=4))
print(items)
