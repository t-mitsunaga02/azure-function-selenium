import logging
from .classfile import Scrape

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    ## Dockerにあるchromedriverを使用
    service = Service(executable_path=r"/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():
        logging.info("data:")
        logging.info(f"{row['BRAND']} {row['Item']}")

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

        logging.info("検索URL:")
        logging.info(first_link)

        ### URLリスト用に加工
        parsed_url = urlparse(first_link).path
        urllist_word = parsed_url[6:17].strip("/")
        search_urllist = f"https://review.kakaku.com/review/{urllist_word}/#tab"

        logging.info("リストURL:")
        logging.info(search_urllist)

        #DataFrameに登録
        columns = ['ID','BRAND','Item','URL']
        values = [row['ID'],row['BRAND'],row['Item'],search_urllist] 
        scr.add_df(values,columns,['<br>'])

    return scr
