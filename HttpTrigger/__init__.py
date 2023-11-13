import logging

import azure.functions as func
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import pandas as pd
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
  

def main(req: func.HttpRequest) -> func.HttpResponse:

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=r"/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get('http://abehiroshi.la.coocan.jp/')
    links = driver.find_elements(By.TAG_NAME, "a")
    logging.warn(links)
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
        else:
            link_list = link_list + ", " + link.text


    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    csv_buffer = io.StringIO()
    link_list.to_csv(csv_buffer, encoding='utf_8', index=False)


    # # create blob service client and container client
    # credential = DefaultAzureCredential()
    # storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    # client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = "testscrape" + str(datetime.now()) + ".txt"

    logging.warn(link_list)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client("scrapefile", blob=blob_name)

    blob_client.upload_blob(link_list)

    return func.HttpResponse(
             str(link_list),
             status_code=200
    )