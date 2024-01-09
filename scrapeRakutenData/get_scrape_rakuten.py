import logging
from .class_file import Scrape

import time
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
import os
import datetime
import requests

#スクレイピングの関数を定義する
def get_scrape_rakuten(url_data):
    scr = Scrape(wait=2,max=5)

    # エラー出力用に実行中のファイル名を取得する
    file_path = os.path.abspath(__file__)
    file_name = os.path.basename(file_path)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # BLOB入出力先の設定
    container_name = "scrapefile"
    blob_name_diff_out_tmp = "dashboard_motive/modify/scraperakutendata_tmp.csv"
    blob_name_diff_out = "dashboard_motive/scraperakutendata.csv"

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        ## ページがあるだけループする
        for n in range(1,1000):
            #商品の指定ページのURLを生成
            target = f"https://review.rakuten.co.jp/search/{row['Item']}/204519/d0-p{n}-t1/"
            print(f'get：{target}')
            logging.info(f"get：{row['Item']}：{target}")

            #ページ内のレビュー記事を一括取得
            try:
                soup = scr.request(target)
            except requests.exceptions.HTTPError as e_rrh:
                # エラー内容を出力し、処理を抜ける
                logging.info(f"rakuten,{row['Item']},{datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')},{file_name},{e_rrh}")
                break

            #ページ内のレビューを全て取得(1ページ30レビュー)
            reviews = soup.find_all('table',width="100%",border="0",cellspacing="0",cellpadding="10")
            print(f'レビュー数:{len(reviews)}')
            logging.info(f'レビュー数:{len(reviews)}')

            #ページ内容レビュー記事の内容をループで全て取得
            for review in reviews:
                try:
                    # 日付は「2023年02月05日 12:10」という形式で取得されるので、日付部分の文字列のみ抽出
                    date = scr.get_text(review.find('td',style="text-align:right"))
                    date = date[:date.find('日')+1]
                    # 評価は「評価  5.00」という記述のされ方なので、数値のみを取得
                    star = scr.get_text(review.find('span',style="color: #f60;"))
                    star = star[4:]

                    title = scr.get_text(review.find('font',size="-1",color="#666666"))
                    comment = scr.get_text(review.find('font',class_='ratCustomAppearTarget'))
                except requests.exceptions.RequestException as e_req:
                    # エラー内容を出力し、後続の処理実行
                    logging.info(f"rakuten,{row['Item']},{datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')},{file_name},{e_req}")
                    continue

                #CSV出力用のDFに登録
                scr.add_df([str(row['POS_ID']),row['Item'],"楽天",date,star,title,comment],['pos_id','item','site_name','review_date','star','title','comment'],['\n'])

            # タグの製品名内の空白が「+」であるため文字列変換
            if ' ' in row['Item'] :
                item_replace = str(row['Item']).replace(' ', '+')
            else :
                item_replace = row['Item']
            #次のページが存在するかチェック（「件数が30未満」または「「次へ」の表示がない」場合は最終ページと判断）
            target2 = f"https://review.rakuten.co.jp/search/{item_replace}/204519/d0-p{n+1}-t1/"
            next = scr.get_text(soup.find('a',href = target2,style ="font-weight:bold;"))
            if (len(reviews) < 30) or (len(next) < 2 ):
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
