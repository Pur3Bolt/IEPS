import json
import re


f = open("strani/overstock.com/jewelry01.html", "r")
s = f.read()
sr = s.replace("\n", '')
title_overstock = '<td valign="top"> \n<a href=".+"><b>(.+?)</b></a>'
listprice_overstock = '<tr><td align="right" nowrap="nowrap"><b>List Price:</b></td><td align="left" nowrap="nowrap"><s>(\$\d+,?\d+\.\d+)</s></td></tr>'
price_overstock = '<tr><td align="right" nowrap="nowrap"><b>Price:</b></td><td align="left" nowrap="nowrap"><span class="bigred"><b>(\$\d+\.\d+)</b></span></td></tr>'
saving_overstock = '<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">(\$\d+,?\d+\.\d+).*</span></td></tr>'
savingPercent_overstock = '<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">.* \((\d+%)\)</span></td></tr>'
# content_overstock = '<td valign="top"><span class="normal">([\S\s]+?)</span><br> \n</td>'
re_title = re.findall(title_overstock, s)
re_listprice = re.findall(listprice_overstock, s)
re_price = re.findall(price_overstock, s)
re_saving = re.findall(saving_overstock, s)
re_savingPercent = re.findall(savingPercent_overstock, s)
items = {}
for i in range(len(re_title)):
    items[i+1] = {
        'Title': re_title[i],
        'ListPrice': re_listprice[i],
        'Price': re_price[i],
        'Saving': re_saving[i],
        'SavingPercent': re_savingPercent[i],
        'Content': ''
    }
print(json.dumps(items, indent=4))
