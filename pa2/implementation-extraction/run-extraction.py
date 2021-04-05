import sys
import json
from regex_extractor import RegexExtractor


# algorithm = sys.argv[1]
algorithm = 'A'
if algorithm == 'A':
    # Overstock
    overstock = {
        'Title': ['<td valign="top"> \n<a href=".+"><b>(.+?)</b></a>', False],
        'ListPrice': ['<tr><td align="right" nowrap="nowrap"><b>List Price:</b></td><td align="left" nowrap="nowrap"><s>(\$\d+,?\d+\.\d+)</s></td></tr>', False],
        'Price': ['<tr><td align="right" nowrap="nowrap"><b>Price:</b></td><td align="left" nowrap="nowrap"><span class="bigred"><b>(\$\d+\.\d+)</b></span></td></tr>', False],
        'Saving': ['<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">(\$\d+,?\d+\.\d+).*</span></td></tr>', False],
        'SavingPercent': ['<tr><td align="right" nowrap="nowrap"><b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">.* \((\d+%)\)</span></td></tr>', False],
        'Content': ['<td valign="top"><span class="normal">([\S\s]+?)</span>', False]
    }
    rgx1 = RegexExtractor('../input-extraction/overstock.com/jewelry01.html', multiple=overstock)
    rgx2 = RegexExtractor('../input-extraction/overstock.com/jewelry02.html', multiple=overstock)
    print(rgx1.extract())
    print(rgx2.extract())

    # RTV Slo
    rtv = {
        'Author': ['<div class="author-name">(.+?)</div>', False],
        'PublishedTime': ['<div class="publish-meta">[\n\t]*(.+?)<br>', False],
        'Title': ['<h1>(.+?)</h1>', False],
        'SubTitle': ['<div class="subtitle">(.+?)</div>', False],
        'Lead': ['<p class="lead">(.+?)</p>', False],
        'Content': ['<div class="article-body">(.+?)</div>[\n\t]*<div class="article-column">', True]
    }
    rgx3 = RegexExtractor('../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html', single=rtv)
    rgx4 = RegexExtractor('../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html', single=rtv)
    print(rgx3.extract())
    print(rgx4.extract())

    # Steam Store
    steam_single = {
        'Title': ['<b>Title:</b> +(.+?) <br>', False],
        'BundleDiscount': ['<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_pct">(.+?)</div>', False],
        'FullPrice': ['<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_original_price">(.+?)</div>', False],
        'BundlePrice': ['<div class="discount_block game_purchase_discount" data-price-final="\d+">.*<div class="discount_original_price">(.+?)</div>', False],
        'Description': ['<h2>About this bundle</h2>[\n\t]*<p>(.+?)</p>', True],
        'BundleSavings': ['<div id="package_savings_bar">[\n\t]*<div class="savings bundle_savings">(.+?)</div>', False]
    }
    steam_multiple = {
        'GameTitle': ['<div class="tab_item_name">(.+?)</div>', False],
        'GameCategories': ['<span class="platform_img .*"></span>[\n\t]*&nbsp; (.+?)</div>', False],
        'GameDiscount': ['<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_pct">(.+?)</div>', False],
        'GameFullPrice': ['<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_prices"><div class="discount_original_price">(.+?)</div>', False],
        'GameDiscountedPrice': ['<div class="discount_block tab_item_discount" data-price-final="\d+">.*<div class="discount_prices">.*<div class="discount_final_price">(.+?)</div>', False],
    }
    rgx5 = RegexExtractor('../input-extraction/store.steampowered.com/Save 37% on peperoncino Bundle on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    rgx6 = RegexExtractor('../input-extraction/store.steampowered.com/Save 59% on Two Point Hospital_ Healthy Collection Vol. 4 on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    print(rgx5.extract())
    print(rgx6.extract())
elif algorithm == 'B':
    pass
elif algorithm == 'C':
    pass
else:
    print('Invalid parameter', algorithm)
    print('Allowed parameter: A, B or C')