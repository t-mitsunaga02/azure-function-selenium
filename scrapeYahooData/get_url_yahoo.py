import logging
from .class_file import Scrape

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException #要素が見つからなかった時用
import time
import random
import os
import datetime
import pandas as pd
from urllib.parse import urlparse

def get_url_yahoo(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # エラー出力用に実行中のファイル名を取得する
    file_path = os.path.abspath(__file__)
    file_name = os.path.basename(file_path)

    # 2.各サイトURL検索

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## seleniumにてブラウザ操作するための準備
        driver = scr.get_driver()

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        logging.info(f"処理スタート：{row['Item']}")
        ## Yahoo検索
        ### Googleのトップページを開く
        driver.get(f"https://www.google.com/search?q=https%3A%2F%2Fshopping.yahoo.co.jp+%E2%80%BA+products+{row['BRAND']}+{row['Item']}")

        logging.info(f"get：{driver.current_url}")

        ### 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(random.randint(4,7))

        ### 検索結果のリンクを収集
        links = driver.find_elements(By.CSS_SELECTOR, 'div.MjjYud')
        logging.info(f"検索結果リンク数：{len(links)}")

        #検索結果を１つずつみて、リンク先のドメインがyahooショッピングのproductsカテゴリのページかどうか判定
        for link in links:
            try:
                domain = link.find_element(By.CSS_SELECTOR,'cite.qLRx3b.tjvcx.GvPZzd.cHaqb').text
            except NoSuchElementException:
                domain = ""
            if domain == "https://shopping.yahoo.co.jp › products":
                try:
                    target_url = link.find_element(By.TAG_NAME,'a').get_attribute("href")
                    print(target_url)
                    logging.info(f"該当URL：{target_url}")
                except NoSuchElementException as e:
                    # エラー内容を出力し、後続の処理実行
                    logging.info(f"yahoo,{row['Item']},{datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')},{file_name},{e}")

                #DataFrameに登録
                columns = ['POS_ID','BRAND','Item','ReviewURL']
                values = [row['POS_ID'],row['BRAND'],row['Item'],target_url] 
                scr.add_df(values,columns)
                break
        # webdriverの終了
        driver.quit()
    return scr
