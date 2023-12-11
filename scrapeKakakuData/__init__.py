import logging
from .class_file import Scrape
from .get_pos import get_pos
from .get_url_kakaku import get_url_kakaku
from .get_scrape_kakaku import get_scrape_kakaku

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

    # 2.価格コムURL検索
    url_data_kakaku = get_url_kakaku(pos_data)
    logging.info("URLkakaku:")
    logging.info(url_data_kakaku.df)
    print(url_data_kakaku.df.head())

    # 3.価格コムスクレイピング
    scrape_data_kakaku = get_scrape_kakaku(url_data_kakaku.df)
    logging.info("scrapekakaku:")
    logging.info(scrape_data_kakaku.df)
    print(scrape_data_kakaku.df.head())

    # 4.CSVファイルに口コミを出力
    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    csv_buffer = io.StringIO()
    scrape_data_kakaku.df.to_csv(csv_buffer, encoding='utf_8', index=False)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
        
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client("scrapefile", "dashboard_motive/raw/scrapekakakudata.csv")
        
    # Upload the created file
    blob_client.upload_blob(csv_buffer.getvalue(), blob_type="BlockBlob", overwrite=True)


    # # Blobへのアップロード
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_out)
    # blob_client.upload_blob(link_list)


    return func.HttpResponse(
                status_code=200
    )