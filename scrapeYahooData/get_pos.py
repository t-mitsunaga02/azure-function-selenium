import logging
from .classfile import Scrape

from azure.storage.blob import BlobServiceClient
import pandas as pd
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

    ## 対象製品の選定
    df_raw = df.filter(items=['ID','Item', 'BRAND'])
    df_fix = df_raw[df_raw['Item'] != 'Suppressed']

    logging.info("Datafix:")
    logging.info(df_fix.head())

    return df_fix
