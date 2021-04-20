import sys
from regex_extractor import RegexExtractor
from xpath_extractor import XPathExtractor
# import json


algorithm = sys.argv[1].upper()
if algorithm == 'A':
    # Overstock
    overstock = {
        'Title': ['<td valign="top"> \n<a href=".+"><b>(.+?)</b></a>', False],
        'ListPrice': ['List Price:</b></td><td[^>]*><s>(\$\d+,?\d+\.\d+)</s>', False],
        'Price': ['Price:</b></td><td[^>]*><span class="bigred"><b>(\$\d+\.\d+)</b>', False],
        'Saving': ['You Save:</b></td><td[^>]*><span class="littleorange">(\$\d+,?\d+\.\d+)', False],
        'SavingPercent': ['You Save:</b></td><td[^>]*><span class="littleorange">.* \((\d+%)\)</span>', False],
        'Content': ['<td valign="top"><span class="normal">([\S\s]+?)<br>', False]
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
        'Content': ['<article class="article">.*?</figure>(.+?)</article>', True]
    }
    rgx3 = RegexExtractor('../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html', single=rtv, cleanup_content=True)
    rgx4 = RegexExtractor('../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html', single=rtv, cleanup_content=True)
    print(rgx3.extract())
    print(rgx4.extract())

    # Steam Store
    steam_single = {
        'Title': ['<b>Title:</b> +(.+?) <br>', False],
        'BundleDiscount': ['<div class=".*game_purchase_discount"[^>]*>.*<div class="discount_pct">-(.+?)</div>', False],
        'FullPrice': ['<div class=".*game_purchase_discount"[^>]*>.*<div class="discount_original_price">(.+?)</div>', False],
        'BundlePrice': ['<div class=".*game_purchase_discount"[^>]*>.*<div class="discount_final_price">(.+?)</div>', False],
        'Description': ['<h2>About this bundle</h2>[\n\t]*<p>(.+?)</p>', True],
        'BundleSavings': ['bundle_savings">(.+?)</div>', False]
    }
    steam_multiple = {
        'GameTitle': ['<div class="tab_item_name">(.+?)</div>', False],
        'GameCategories': ['<span class="platform_img .*"></span>[\n\t]*&nbsp; (.+?)</div>', False],
        'GameDiscount': ['<div class=".*tab_item_discount"[^>]*>.*<div class="discount_pct">-(.+?)</div>', False],
        'GameFullPrice': ['<div class=".*tab_item_discount"[^>]*>.*<div class="discount_prices"><div class="discount_original_price">(.+?)</div>', False],
        'GameDiscountedPrice': ['<div class=".*tab_item_discount"[^>]*>.*<div class="discount_prices">.*<div class="discount_final_price">(.+?)</div>', False],
    }
    rgx5 = RegexExtractor('../input-extraction/store.steampowered.com/Save 37% on peperoncino Bundle on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    rgx5.extract()
    rgx5.replace_br('Description')
    rgx6 = RegexExtractor('../input-extraction/store.steampowered.com/Save 59% on Two Point Hospital_ Healthy Collection Vol. 4 on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    rgx6.extract()
    rgx6.replace_br('Description')
    print(rgx5.extract())
    print(rgx6.extract())
elif algorithm == 'B':
    # Overstock
    overstock = {
        'Title': '//td[@valign="top"]/a/b/text()',
        'ListPrice': '//td[@align="left"][@nowrap]/s/text()',
        'Price': '//span[@class="bigred"]/b/text()',
        'Saving': '//td[@align="left"]/span[@class="littleorange"]/substring-before(text(), " (")',
        'SavingPercent': '//td[@align="left"]/span[@class="littleorange"]/substring-before(substring-after(text(), " ("), ")")',
        'Content': '//span[@class="normal"]/text()',
    }
    xp1 = XPathExtractor('../input-extraction/overstock.com/jewelry01.html', multiple=overstock)
    xp2 = XPathExtractor('../input-extraction/overstock.com/jewelry02.html', multiple=overstock)
    print(xp1.extract())
    print(xp2.extract())

    # RTV Slo
    rtv = {
        'Author': '//div[@class="author-name"]/text()',
        'PublishedTime': '//div[@class="publish-meta"]/text()',
        'Title': '//h1/text()',
        'SubTitle': '//div[@class="subtitle"]/text()',
        'Lead': '//p[@class="lead"]/text()',
        'Content': ['//article/p/descendant-or-self::*/text()', XPathExtractor.JOIN_ALL]
    }
    xp3 = XPathExtractor('../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html', single=rtv)
    xp4 = XPathExtractor('../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html', single=rtv)
    print(xp3.extract())
    print(xp4.extract())

    # Steam Store
    steam_single = {
        'Title': ['//div[@class="details_block"]/p/descendant-or-self::text()[not(ancestor::b) and normalize-space(.) != ""]', XPathExtractor.FORCE_LXML],
        'BundleDiscount': '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_pct"]/text()',
        'FullPrice': '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()',
        'BundlePrice': '//div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()',
        'Description': ['//*[@id="game_area_description"]/p/text()', XPathExtractor.JOIN_ALL],
        'BundleSavings': '//div[contains(@class, "bundle_savings")]/text()',
    }
    steam_multiple = {
        'GameTitle': '//div[@class="tab_item_name"]/text()',
        'GameCategories': '//div[@class="tab_item_details"]/text()',
        'GameDiscount': '//div[@class="discount_block tab_item_discount"]/div[@class="discount_pct"]/text()',
        'GameFullPrice': '//div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_original_price"]/text()',
        'GameDiscountedPrice': '//div[@class="discount_block tab_item_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()',
    }
    xp5 = XPathExtractor('../input-extraction/store.steampowered.com/Save 37% on peperoncino Bundle on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    xp6 = XPathExtractor('../input-extraction/store.steampowered.com/Save 59% on Two Point Hospital_ Healthy Collection Vol. 4 on Steam.html', single=steam_single, multiple=steam_multiple, multiple_title='Games')
    print(xp5.extract())
    print(xp6.extract())
elif algorithm == 'C':
    pass
else:
    print('Invalid parameter', algorithm)
    print('Allowed: A, B or C')