import logging
from .class_file import Scrape

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from urllib.parse import urlparse

def get_url_kakaku(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 2.各サイトURL検索
    ## seleniumにてブラウザ操作するための準備
    driver = scr.get_driver()

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        ## 価格コム検索
        ### Googleのトップページを開く
        driver.get("https://www.google.com")

        ### 検索ボックスを見つける
        search_box = driver.find_element(By.NAME, "q")

        ### 検索ワードを入力し、Enterキーを押して検索を実行
        search_box.send_keys("価格" + search_word)
        search_box.send_keys(Keys.RETURN)

        ### 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(3)

        ### 最初の検索結果のリンクを取得
        first_result = driver.find_element(By.CSS_SELECTOR, "h3")
        first_link = first_result.find_element(By.XPATH, '..').get_attribute('href')

        ### URLリスト用に加工(口コミ・製品情報ともに取得)
        parsed_url = urlparse(first_link).path
        urllist_word = parsed_url[6:17].strip("/")
        search_urllist = f"https://review.kakaku.com/review/{urllist_word}/#tab"
        search_urllist_product = f"https://kakaku.com/item/{urllist_word}/spec/#tab"

        logging.info("リストURL:")
        logging.info(search_urllist)
        logging.info(search_urllist_product)

        #DataFrameに登録
        columns = ['POS_ID','BRAND','Item','ReviewURL','ProductURL']
        values = [row['POS_ID'],row['BRAND'],row['Item'],search_urllist,search_urllist_product] 
        scr.add_df(values,columns)

    return scr
