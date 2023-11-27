import logging
from .classfile import Scrape

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from urllib.parse import urlparse

def get_url_amazon(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 2.各サイトURL検索
    ## seleniumにてブラウザ操作するための準備
    driver = scr.get_driver()

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        ## Amazon検索
        ### GoogleからAmazonの検索ページを検索する
        driver.get(f"https://www.google.com/search?q=https://www.amazon.co.jp/s?k={row['BRAND']}+{row['Item']}")

        ### 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(3)

        ### 検索結果のリンクを収集
        links = driver.find_elements(By.CSS_SELECTOR, "div.MjjYud")

        #検索結果を１つずつみて、リンク先のURLを抽出
        for link in links:

            logging.info("link:")
            logging.info(link)
            ## 製品名を含まないなら除外
            if row['Item'] not in link:
                break
            logging.info("1")
            ## 製品ページのパスがないなら除外
            if "/dp/" not in link:
                break
            logging.info("2")
            ## 英語ページなら除外
            if "/-/en/" in link:
                break
            logging.info("3")
            ## フィルタ製品ページなら除外
            if "フィルタ―" in link:
                break
            logging.info("4")

            parsed_url = urlparse(link).path

            # 検索文字列の位置を見つける
            pos = parsed_url.find("/dp/")

            asinID = link[pos + len("/dp/"): pos + len("/dp/") + 10]

            #DataFrameに登録
            columns = ['ID','BRAND','Item','asinID']
            values = [row['ID'],row['BRAND'],row['Item'],asinID] 
            scr.add_df(values,columns)

    return scr
