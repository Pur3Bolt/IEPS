import json
import re


f = open("strani/store.steampowered.com/Save 37% on peperoncino Bundle on Steam.html", "r", encoding='utf-8')
s = f.read()
bundle_title = '<b>Title:</b> +(.+?) <br>'
bundle_discount = '<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_pct">(.+?)</div>'
full_price = '<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_original_price">(.+?)</div>'
bundle_price = '<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_final_price">(.+?)</div>'
description = '<h2>About this bundle</h2>[\n\t]*<p>(.+?)</p>'  # single line
bundle_savings = '<div id="package_savings_bar">[\n\t]*<div class="savings bundle_savings">(.+?)</div>'
game_title = '<div class="tab_item_name">(.+?)</div>'
game_categories = '<span class="platform_img .*"></span>[\n\t]*&nbsp; (.+?)</div>'
game_discount = '<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_pct">(.+?)</div>'
game_full_price = '<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_prices"><div class="discount_original_price">(.+?)</div>'
game_discounted_price = '<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_prices">.*<div class="discount_final_price">(.+?)</div>'

re_bundle_title = re.findall(bundle_title, s)
re_bundle_discount = re.findall(bundle_discount, s)
re_full_price = re.findall(full_price, s)
re_bundle_price = re.findall(bundle_price, s)
re_description = re.findall(description, s, re.DOTALL)
if len(re_description) == 0:
    re_description.append("")
re_bundle_savings = re.findall(bundle_savings, s)

re_game_title = re.findall(game_title, s)
re_game_categories = re.findall(game_categories, s)
re_game_discount = re.findall(game_discount, s)
re_game_full_price = re.findall(game_full_price, s)
re_game_discounted_price = re.findall(game_discounted_price, s)

items = {
    'Title': re_bundle_title[0],
    'BundleDiscount': re_bundle_discount[0],
    'FullPrice': re_full_price[0],
    'BundlePrice': re_bundle_price[0],
    'Description': re_description[0],
    'BundleSavings': re_bundle_savings[0],
}
games = []
for i in range(len(re_game_title)):
    games.append({
        'GameTitle': re_game_title[i],
        'GameCategories': re_game_categories[i],
        'GameDiscount': re_game_discount[i],
        'GameFullPrice': re_game_full_price[i],
        'GameDiscountedPrice': re_game_discounted_price[i],
    })
items['Games'] = games
print(json.dumps(items, indent=4))
# print(items)
