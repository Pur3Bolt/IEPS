import json
from lxml import html
import elementpath


f = open("input-extraction/store.steampowered.com/Save 37% on peperoncino Bundle on Steam.html", "r", encoding='utf-8')
s = f.read()
tree = html.fromstring(s)

bundle_title = '//div[@class="details_block"]/p/descendant-or-self::text()[not(ancestor::b) and normalize-space(.) != ""]'
bundle_discount = '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_pct"]/text()'
full_price = '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()'
bundle_price = '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()'
description = '//*[@id="game_area_description"]/p/text()'
bundle_savings = '//div[@class="savings bundle_savings"]/text()'
game_title = '//div[@class="tab_item_name"]/text()'
game_categories = '//div[@class="tab_item_details"]/text()'
game_discount = '//div[@class="discount_block tab_item_discount"]/div[@class="discount_pct"]/text()'
game_full_price = '//div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()'
game_discounted_price = '//div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()'

xp_bundle_title = tree.xpath(bundle_title)
xp_bundle_discount = tree.xpath(bundle_discount)
xp_full_price = tree.xpath(full_price)
xp_bundle_price = tree.xpath(bundle_price)
xp_description = tree.xpath(description)
xp_bundle_savings = tree.xpath(bundle_savings)

xp_game_title = tree.xpath(game_title)
xp_game_categories = tree.xpath(game_categories)
xp_game_discount = tree.xpath(game_discount)
xp_game_full_price = tree.xpath(game_full_price)
xp_game_discounted_price = tree.xpath(game_discounted_price)

items = {
    'Title': xp_bundle_title[0].strip(),
    'BundleDiscount': xp_bundle_discount[0],
    'FullPrice': xp_full_price[0],
    'BundlePrice': xp_bundle_price[0],
    'Description': ''.join(xp_description),
    'BundleSavings': xp_bundle_savings[0],
}
games = []
for i in range(len(xp_game_title)):
    games.append({
        'GameTitle': xp_game_title[i],
        'GameCategories': xp_game_categories[i].strip(),
        'GameDiscount': xp_game_discount[i],
        'GameFullPrice': xp_game_full_price[i],
        'GameDiscountedPrice': xp_game_discounted_price[i],
    })
items['Games'] = games
print(json.dumps(items, indent=4))
# print(items)
