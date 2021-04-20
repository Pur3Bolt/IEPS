import json
import re


f = open("input-extraction/overstock.com/jewelry01.html", "r")
s = f.read()
title = '<td valign="top"> \n<a href=".+"><b>(.+?)</b></a>'
listprice = '<td[^>]*><s>(\$\d+,?\d+\.\d+)</s>'
price = '<span class="bigred"><b>(\$\d+\.\d+)</b>'
saving = 'You Save:</b></td><td[^>]*><span[^>]*>(\$\d+,?\d+\.\d+)'
saving_percent = 'You Save:</b></td><td[^>]*><span[^>]*>.* \((\d+%)\)</span>'
content = '<span class="normal">([\S\s]+?)<br>'
re_title = re.findall(title, s)
re_list_price = re.findall(listprice, s)
re_price = re.findall(price, s)
re_saving = re.findall(saving, s)
re_saving_percent = re.findall(saving_percent, s)
re_content = re.findall(content, s)
items = {}
for i in range(len(re_title)):
    items[i+1] = {
        'Title': re_title[i],
        'ListPrice': re_list_price[i],
        'Price': re_price[i],
        'Saving': re_saving[i],
        'SavingPercent': re_saving_percent[i],
        'Content': re_content[i],
    }
print(json.dumps(items, indent=4))
# print(items)
