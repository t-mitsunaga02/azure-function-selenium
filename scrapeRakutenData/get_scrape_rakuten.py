import logging
from .class_file import Scrape

import time
from urllib.parse import urlparse

#スクレイピングの関数を定義する
def get_scrape_rakuten(url_data):
    scr = Scrape(wait=2,max=5)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        ## ページがあるだけループする
        for n in range(1,1000):
            #商品の指定ページのURLを生成
            #if文で場合分け
            target = f"https://review.rakuten.co.jp/search/{row['Item']}/204519/d0-p{n}-t1/"
            print(f'get：{target}')
            logging.info(f"get：{row['Item']}：{target}")

            #ページ内のレビュー記事を一括取得
            soup = scr.request(target)

            #ページ内のレビューを全て取得(1ページ30レビュー)
            reviews = soup.find_all('table',width="100%",border="0",cellspacing="0",cellpadding="10")
            print(f'レビュー数:{len(reviews)}')
            logging.info(f'レビュー数:{len(reviews)}')

            #ページ内容レビュー記事の内容をループで全て取得
            for review in reviews:
                # 日付は「2023年02月05日 12:10」という形式で取得されるので、日付部分の文字列のみ抽出
                date = scr.get_text(review.find('td',style="text-align:right"))
                date = date[:date.find('日')+1]
                # 評価は「評価  5.00」という記述のされ方なので、数値のみを取得
                star = scr.get_text(review.find('span',style="color: #f60;"))
                star = star[4:]

                title = scr.get_text(review.find('font',size="-1",color="#666666"))
                comment = scr.get_text(review.find('font',class_='ratCustomAppearTarget'))

                #CSV出力用のDFに登録
                scr.add_df([str(row['POS_ID']),row['Item'],"楽天",date,star,title,comment],['pos_id','item','site_name','review_date','star','title','comment'],['\n'])

            # タグの製品名内の空白が「+」であるため文字列変換
            if ' ' in row['Item'] :
                item_replace = str(row['Item']).replace(' ', '+')
            #次のページが存在するかチェック（「件数が30未満」または「「次へ」の表示がない」場合は最終ページと判断）
            target2 = f"https://review.rakuten.co.jp/search/{item_replace}/204519/d0-p{n+1}-t1/"
            next = scr.get_text(soup.find('a',href = target2,style ="font-weight:bold;"))
            if (len(reviews) < 30) or (len(next) < 2 ):
                break

    #コメントが重複するレコードを削除する
    scr = scr.df.drop_duplicates(subset=['pos_id', 'site_name', 'review_date', 'comment'])

    #スクレイプ結果をCSVに出力
    return scr
