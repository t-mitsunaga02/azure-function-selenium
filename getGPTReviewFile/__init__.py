import logging
import json
from .get_chatgpt import scrape_gpt_get
from .chatgpt_merge import gpt_modify

import azure.functions as func
import asyncio
import pandas as pd

async def main(req: func.HttpRequest) -> func.HttpResponse:
    func_url = req.url

    logging.info(f"ChatGPTデータ判定処理開始")

    # 非同期で処理を実行
    asyncio.create_task(get_GPT_data())

    # 監視用URLとともに応答を返す
    return func.HttpResponse(
        body=json.dumps({"status": "started", "monitor_url": func_url + "/status"}),
        status_code=202
    )

async def get_GPT_data():
    # 1.GPT判定処理
    gpt_data = scrape_gpt_get()
    logging.info(f"GPT:{gpt_data}")
    print(f"GPT:{gpt_data}")

    # 2.購入動機判定データ蓄積前処理
    motive_data = gpt_modify(gpt_data)
    logging.info(f"Motive:{motive_data}")
    print(f"Motive:{motive_data}")
