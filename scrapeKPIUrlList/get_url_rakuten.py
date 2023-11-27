import logging
from .classfile import Scrape
from urllib.parse import urlparse

def get_url_rakuten(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 2.各サイトURL検索

    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['Item']}"

        ## 楽天製品口コミページURL生成
        search_urllist = f"https://review.rakuten.co.jp/search/{search_word}/204519/d0-t1/"

        logging.info("リストURL:")
        logging.info(search_urllist)

        #DataFrameに登録
        columns = ['ID','BRAND','Item','ReviewURL']
        values = [row['ID'],row['BRAND'],row['Item'],search_urllist] 
        scr.add_df(values,columns)

    return scr
