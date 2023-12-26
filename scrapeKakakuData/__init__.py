import logging
import json
from .class_file import Scrape
from .get_pos import get_pos
from .get_url_kakaku import get_url_kakaku
from .get_scrape_kakaku import get_scrape_kakaku

import azure.functions as func
from azure.storage.blob import BlobServiceClient
import asyncio
import pandas as pd
import io
import os

async def main(req: func.HttpRequest) -> func.HttpResponse:
    func_url = req.url

    logging.info(f"価格コムスクレイピング処理開始")

    # 非同期で処理を実行
    asyncio.create_task(scrape_kakaku())

    # 監視用URLとともに応答を返す
    return func.HttpResponse(
        body=json.dumps({"status": "started", "monitor_url": func_url + "/status"}),
        status_code=202
    )

async def scrape_kakaku():
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
    logging.info(scrape_data_kakaku)
    print(scrape_data_kakaku.head())
