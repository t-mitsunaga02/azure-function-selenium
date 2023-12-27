import logging
from .class_file import Scrape

import time
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
import os

#スクレイピングの関数を定義する
def get_scrape_kakaku(url_data):
    scr = Scrape(wait=2,max=5)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # BLOB入出力先の設定
    container_name = "scrapefile"
    blob_name_diff_out_tmp = "dashboard_motive/scrapekakakudata_tmp.csv"
    blob_name_diff_out = "dashboard_motive/raw/scrapekakakudata.csv"

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        #レビューのURLから商品IDの手前までを取り出す
        url = row['ReviewURL'][:row['ReviewURL'].find('#tab')]

        for n in range(1,1000):
            #商品の指定ページのURLを生成
            target = url+f'?Page={n}#tab'
            print(f'get：{target}')
            logging.info(f"get：{row['Item']}：{target}")
    
            #レビューページの取得
            soup = scr.request(target)
            time.sleep(3)

            print(row['Item'])

            #ページ内のレビュー記事を一括取得
            reviews = soup.find_all('div',class_='revMainClmWrap')
            #ページ内のすべてと評価を一括取得
            evals = soup.find_all('div',class_='reviewBoxWtInner')
            
            # ページ送り終了条件の準備
            next_page = ""
            a_tag = soup.find('a', string='次のページへ')

            print(f'レビュー数:{len(reviews)}')
            logging.info(f'レビュー数:{len(reviews)}')
            
            #ページ内の全てのレビューをループで取り出す
            for review,eval in zip(reviews,evals):
                #レビューのタイトルを取得
                title = scr.get_text(review.find('div',class_='reviewTitle'))
                #レビューの内容を取得
                comment = scr.get_text(review.find('p',class_='revEntryCont')).replace('<br>','')
    
                #満足度（デザイン、処理速度、グラフィック性能、拡張性、・・・・・の値を取得
                tables = eval.find_all('table')
                star = scr.get_text(tables[0].find('td'))
                date = scr.get_text(eval.find('p',class_='entryDate clearfix'))
                date = date[:date.find('日')+1]
    
                columns = ['pos_id','item','site_name','review_date','star','title','comment']
                values = [str(row['POS_ID']),row['Item'],"価格コム",date,star,title,comment] 
                
                #DataFrameに登録
                scr.add_df(values,columns)

            # ページ送りの終了条件判定
            if a_tag:
                next_page = a_tag.get('href')

            #ページ内のレビュー数が15未満なら、最後のページと判断してループを抜ける
            if len(reviews) < 15 or next_page == "":
                break

        # データをCSVファイルとして出力 
        output_blob_client_tmp = blob_service_client.get_blob_client(container=container_name, blob=blob_name_diff_out_tmp)
        output_blob_client_tmp.upload_blob(scr.df.to_csv(index=False, encoding='utf_8'), blob_type="BlockBlob", overwrite=True)
            
    #コメントが重複するレコードを削除する
    scr_dup = scr.df.drop_duplicates(subset=['pos_id', 'site_name', 'review_date', 'comment'])
    # 重複削除後再アップロード
    output_blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name_diff_out)
    output_blob_client.upload_blob(scr_dup.to_csv(index=False, encoding='utf_8'), blob_type="BlockBlob", overwrite=True)

    #スクレイプ結果をCSVに出力
    return scr_dup
