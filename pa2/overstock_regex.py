import json
import re


f = open("strani/overstock.com/jewelry02.html", "r")
s = f.read()
title = '<td valign="top"> \n<a href=".+"><b>(.+?)</b></a>'
listprice = '<tr><td align="right" nowrap="nowrap"><b>List Price:</b></td><td align="left" nowrap="nowrap"><s>(\$\d+,?\d+\.\d+)</s></td></tr>'
price = '<tr><td align="right" nowrap="nowrap"><b>Price:</b></td><td align="left" nowrap="nowrap"><span class="bigred"><b>(\$\d+\.\d+)</b></span></td></tr>'
saving = '<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">(\$\d+,?\d+\.\d+).*</span></td></tr>'
saving_percent = '<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">.* \((\d+%)\)</span></td></tr>'
content = '<td valign="top"><span class="normal">([\S\s]+?)</span>'
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
