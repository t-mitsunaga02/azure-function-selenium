import logging
from .classfile import Scrape

import azure.functions as func
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import time
import pandas as pd
from urllib.parse import urlparse
import os
import io

def get_pos():
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 1.POSデータの読み込み
    ## BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    ## Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    ## BLOB入出力先の設定
    container_name = "scrapefile"
    blob_name_in = "dashboard_KPI/modify/data/KPI_modify_POS_master_file.csv"

    ## POSデータ取得
    blob_client_in = blob_service_client.get_blob_client(container=container_name, blob=blob_name_in)
    blob_data = blob_client_in.download_blob()
    pos_data = blob_data.readall()

    ## DataFrame化
    df = pd.read_csv(io.BytesIO(pos_data))
    logging.info("DataFrame:")
    logging.info(df.head())

    ## 対象製品の選定
    df_raw = df.filter(items=['ID','Item', 'BRAND'])
    df_fix = df_raw[df_raw['Item'] != 'Suppressed']

    logging.info("Datafix:")
    logging.info(df_fix.head())

## 出力確認用
    df_string = df_fix.to_string()
    logging.info("DataFrameall:")
    logging.info(df_string)

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
    for index, row in df_fix.iterrows():
        logging.info("data:")
        logging.info(f"{row['BRAND']} {row['Item']}")

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"
        logging.info("word:")
        logging.info(search_word)

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

    return search_urllist






    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    # csv_buffer = io.StringIO()
    # link_list.to_csv(csv_buffer, encoding='utf_8', index=False)

    # logging.warn(link_list)

    # # Blobへのアップロード
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_out)
    # blob_client.upload_blob(link_list)
