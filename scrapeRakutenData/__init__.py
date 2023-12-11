import logging
from .class_file import Scrape
from .get_pos import get_pos
from .get_url_rakuten import get_url_rakuten
from .get_scrape_rakuten import get_scrape_rakuten

import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os

def main(req: func.HttpRequest) -> func.HttpResponse:

    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 1.POSデータの読み込み
    pos_data = get_pos()
    logging.info("POS:")
    logging.info(pos_data.head())
    print(pos_data.head())

    # 2.楽天URL検索
    url_data_rakuten = get_url_rakuten(pos_data)
    logging.info("URLrakuten:")
    logging.info(url_data_rakuten.df)
    print(url_data_rakuten.df.head())

    # 3.楽天スクレイピング
    scrape_data_rakuten = get_scrape_rakuten(url_data_rakuten.df)
    logging.info("scraperakuten:")
    logging.info(scrape_data_rakuten.df)
    print(scrape_data_rakuten.df.head())

    # 4.CSVファイルに口コミを出力
    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    csv_buffer = io.StringIO()
    scrape_data_rakuten.df.to_csv(csv_buffer, encoding='utf_8', index=False)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
        
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client("scrapefile", "scraperakutendata.csv")
        
    # Upload the created file
    blob_client.upload_blob(csv_buffer.getvalue(), blob_type="BlockBlob", overwrite=True)


    # # Blobへのアップロード
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_out)
    # blob_client.upload_blob(link_list)


    return func.HttpResponse(
                status_code=200
    )