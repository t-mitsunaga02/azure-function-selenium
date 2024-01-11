from .class_file import Scrape
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException #要素が見つからなかった時用
import time
import pandas as pd
from urllib.parse import urlparse

def get_url_amazon(get_pos):
    scr = Scrape(wait=3,max=5)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"
        # Amazon検索
        ## seleniumにてブラウザ操作するための準備
        driver = scr.get_driver()

        ## Amazonの検索ページを表示する
        target = f"https://www.amazon.co.jp/s?k={row['BRAND']}+{row['Item']}&crid=3M1NNK3XMSY5M&sprefix=kc-n50%2Caps%2C174&ref=nb_sb_noss_1"
        print(target)
        driver.get(target)

        ## 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(5)

        ## 製品ページのタグを取得
        products = driver.find_elements(By.CSS_SELECTOR, 'div.sg-col-4-of-24.sg-col-4-of-12.s-result-item.s-asin.sg-col-4-of-16.sg-col.s-widget-spacing-small.sg-col-4-of-20')
        #  first_link = first_result.find_element(By.XPATH, '..').get_attribute('href')

        print(f"製品タイトル数:{len(products)}")

        asin_list = []
        for product in products:
            # 製品タイトルのテキストを取得
            title_element = product.find_element(By.CSS_SELECTOR, 'span.a-size-base-plus.a-color-base.a-text-normal')
            title_text = title_element.text

            # 製品の値段を取得（LEVOITのフィルタ商品を除外するため）
            try:
                money_element = product.find_element(By.CSS_SELECTOR, 'span.a-price-whole')
                money_text = int(money_element.text.replace(',',''))
            except NoSuchElementException:
                money_element = ""

            # 指定された製品名がタイトルに含まれているかチェック
            if scr.normalize_string(row['Item']) not in scr.normalize_string(title_text):
                continue
            # LEVOIT以外はフィルタ―製品除外
            if row['BRAND'] != "LEVOIT":
                ### フィルタ製品じゃないかどうか
                if "フィルタ" in title_text:
                    continue
            else:
                ### LEVOITの場合は値段でフィルタ判断
                if money_text <= 7000 or "用フィルタ" in title_text or "空気清浄機用" in title_text or "交換" in title_text:
                    continue

            print(f"タイトル：{title_text}")
            asin = product.get_attribute("data-asin")
            print(asin)

            ### DataFrameに登録
            columns = ['POS_ID','BRAND','Item','asinID']
            values = [row['POS_ID'],row['BRAND'],row['Item'],asin] 
            scr.add_df(values,columns)
        # WebDriverを閉じる
        driver.quit()

            #     ### 色/スタイルなどの違いがある製品を取得
            #     color_target = f"https://www.amazon.co.jp{asin_url}"
            #     color_soup = scr.request(color_target)
            #     time.sleep(3)

            #     ### エレメントが3種類切り替わるため
            #     color_url_1 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare')
            #     color_url_2 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal dimension-values-list')
            #     color_url_3 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches')

            #     color_url = color_url_1 + color_url_2 + color_url_3

            #     ### 色違い製品がない場合はループを抜ける
            #     if not color_url :
            #         continue

            #     print(f"数:{len(color_url)}")
            #     ### リンク切り替えループ
            #     for urls in color_url:
            #         ### asinID取得
            #         pattern = r"data-csa-c-item-id=.{1}(.{10})"
            #         hits = re.findall(pattern, str(urls))
            #         ### asinID毎に遷移するループ
            #         for asin in hits:
            #             print(asin)
            #             ### asinIDを置換し遷移する
            #             replace_asin = f"/dp/{asin}"
            #             re_asin_url = re.sub(r'/dp/(\w{10})', replace_asin, color_target)
            #             print(re_asin_url)
            #             re_asin_soup = scr.request(re_asin_url)
            #             time.sleep(3)

            #             re_asin_text = re_asin_soup.find('span', class_='a-size-large product-title-word-break')

            #             # print(re_asin_text.text)
            #             if re_asin_text:
            #                 ### 検索した製品と同名かどうか
            #                 if scr.normalize_string(row['Item']) not in scr.normalize_string(re_asin_text.text): 
            #                     continue
            #                 ### フィルタ製品じゃないかどうか
            #                 if "フィルタ" in re_asin_text.text:
            #                     continue
            #                 ### DataFrameに登録
            #                 columns = ['BRAND','Item','asinID']
            #                 values = [row['BRAND'],row['Item'],asin] 
            #                 scr.add_df(values,columns)
            #             else:
            #                 continue
            
            # else:
            #     continue

    return scr
