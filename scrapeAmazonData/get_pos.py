import logging
from class_file import Scrape

import pandas as pd
import io

def get_pos():
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 1.POSデータの読み込み
    #URLリストの読み込み
    df = pd.read_csv('C:/Users/t-mitsunaga/work/ツール/Azure/pythonProject/scrape_test/KPI_modify_POS_master_file.csv')

    ## 対象製品の選定
    df_raw = df.filter(items=['ID','Item', 'BRAND'])
    df_fix = df_raw[df_raw['Item'] != 'Suppressed']

    logging.info("Datafix:")
    logging.info(df_fix.head())

    return df_fix
