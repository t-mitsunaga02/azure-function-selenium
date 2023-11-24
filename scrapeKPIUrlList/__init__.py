import logging

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

#新しいクラス（モジュール）を作る 
class Scrape():
 
    def __init__(self,wait=1,max=None):
        self.response = None
        self.df = pd.DataFrame()
        self.wait = wait
        self.max = max
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
        self.timeout = 5
 
    def to_csv(self,filename,dropcolumns=None):
        '''
        DataFrame をCSVとして出力する
        dropcolumns に削除したい列をリストで指定可能
 
        Params
        ---------------------      
        filename:str
            ファイル名
        dropcolumns:[str]
            削除したい列名            
        '''
        if dropcolumns is not None:
            self.df.drop(dropcolumns,axis=1,inplace=True) 
        self.df.to_csv(filename,index=False,encoding="shift-jis",errors="ignore")

    def add_df(self,values,columns,omits = None):
        '''
        指定した値を　DataFrame に行として追加する
        omits に削除したい文字列をリストで指定可能
 
        Params
        ---------------------      
        values:[str]
            列名
        omits:[str]
            削除したい文字、又は文字列            
        '''
        if omits is not None:
            values = self.omit_char(values,omits)
            columns = self.omit_char(columns,omits)
        
        df = pd.DataFrame(values,index=self.rename_column(columns))
        self.df = pd.concat([self.df,df.T])

    def omit_char(self,values,omits):
        '''
        リストで指定した文字、又は文字列を削除する
 
        Params
        ---------------------      
        values:str
            対象文字列
        omits:str
            削除したい文字、又は文字列            
 
        Returns
        ---------------------
        return :str
            不要な文字を削除した文字列
        '''
        for n in range(len(values)):
            for omit in omits:
                values[n] = values[n].replace(omit,'')
        return values

    def rename_column(self,columns):
        '''
        重複するカラム名の末尾に連番を付与し、ユニークなカラム名にする
            例 ['A','B','B',B'] → ['A','B','B_1','B_2']
 
        Params
        ---------------------      
        columns: [str]
            カラム名のリスト
          
        Returns
        ---------------------
        return :str
            重複するカラム名の末尾に連番が付与されたリスト
        '''
        lst = list(set(columns))
        for column in columns:
            dupl = columns.count(column)
            if dupl > 1:
                cnt = 0
                for n in range(0,len(columns)):
                    if columns[n] == column:
                        if cnt > 0:
                            columns[n] = f'{column}_{cnt}'
                        cnt += 1
        return columns


def main(req: func.HttpRequest) -> func.HttpResponse:

    # 1.POSデータの読み込み
    ## BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    ## Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    ## BLOB入出力先の設定
    container_name = "scrapefile"
    blob_name_in = "dashboard_KPI/modify/data/KPI_modify_POS_master_file.csv"
    blob_name_out = "dashboard_KPI/raw/scrape/URL/testscrape" + str(datetime.now()) + ".csv"

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
        brand_column = row['BRAND']
        item_column = row['Item']
        search_word = brand_column + " " + item_column
        logging.info("word:")
        logging.info(search_word)

        ## 価格コム検索
        ### Googleのトップページを開く
        driver.get("https://www.google.com")

        ### 検索ボックスを見つける
        search_box = driver.find_element_by_name("q")

        ### 検索ワードを入力し、Enterキーを押して検索を実行
        search_box.send_keys("価格" + search_word)
        search_box.send_keys(Keys.RETURN)

        ### 検索結果ページがロードされるのを待つ（例: 5秒待つ）
        time.sleep(5)

        ### 最初の検索結果のリンクを取得
        first_result = driver.find_element_by_css_selector("h3")
        first_link = first_result.find_element_by_xpath('..').get_attribute('href')

        logging.info("検索URL:")
        logging.info(first_link)

        ### URLリスト用に加工
        parsed_url = urlparse(first_link).path
        urllist_word = parsed_url[6].strip("/")
        search_urllist = f"https://review.kakaku.com/review/{urllist_word}/#tab"

        logging.info("リストURL:")
        logging.info(search_urllist)
    






    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    # csv_buffer = io.StringIO()
    # link_list.to_csv(csv_buffer, encoding='utf_8', index=False)

    # logging.warn(link_list)

    # # Blobへのアップロード
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_out)
    # blob_client.upload_blob(link_list)

    return func.HttpResponse(
             #str(link_list),
             status_code=200
    )