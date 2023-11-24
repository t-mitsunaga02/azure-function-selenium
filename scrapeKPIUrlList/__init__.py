import logging
from .classfile import Scrape
from .get_pos import get_pos
from .get_url_kakaku import get_url_kakaku

import azure.functions as func
import pandas as pd

def main(req: func.HttpRequest) -> func.HttpResponse:
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 1.POSデータの読み込み
    pos_data = get_pos()
    logging.info("POS:")
    logging.info(pos_data.head())

    # 2.価格コムURL検索
    url_data_kakaku = get_url_kakaku(pos_data)
    logging.info("URLkakaku:")
    logging.info(url_data_kakaku.df)


    # データフレームをCSV形式の文字列に変換し、その文字列をメモリ上のストリームに書き込む
    # csv_buffer = io.StringIO()
    # link_list.to_csv(csv_buffer, encoding='utf_8', index=False)

    # logging.warn(link_list)

    # # Blobへのアップロード
    # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_out)
    # blob_client.upload_blob(link_list)


    return func.HttpResponse(
             status_code=200
    )