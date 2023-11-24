import logging
from .classfile import Scrape
from .get_pos import get_pos

import azure.functions as func
import pandas as pd

def main(req: func.HttpRequest) -> func.HttpResponse:
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 1.POSデータの読み込み
    geturl = get_pos()
    logging.info("取得URL:")
    logging.info(geturl)


    return func.HttpResponse(
             status_code=200
    )