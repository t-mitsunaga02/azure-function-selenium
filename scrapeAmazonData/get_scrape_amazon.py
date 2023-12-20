import logging
from .class_file import Scrape
import time

def get_scrape_amazon(url_data):
    scr = Scrape(wait=2,max=5)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():
        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        #最大500ページ分（500×10=5000レビュー分）を読み出すループ
        for n in range(1,500):

            #商品IDからレビュー記事のページを生成
            target = f"https://www.amazon.co.jp/product-reviews/{row['asinID']}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&formatType=current_format&pageNumber={n}#reviews-filter-bar"
            #print(f'get：{target}')
            logging.info(f"get：{row['Item']}：{target}")

            #ページを読み込む
            soup = scr.request(target)
            #print(soup)
            time.sleep(3)

            #ページ内のレビューを全て取得(1ページ10レビュー)
            reviews = soup.find_all('div',class_='a-section review aok-relative')
            print(f'ページ数:{n}')
            print(f'レビュー数:{len(reviews)}')
            logging.info(f'レビュー数:{len(reviews)}')

            #レビューの数だけループ
            for review in reviews:
                #日本のレビューアが書いたレビューのタイトルを取得
                title = scr.get_text(review.find('a',class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold'))
                #print(title)
                #外国人のレビューアが書いたレビューのタイトルを取得(日本人と外国人ではタグが異なっていた)
                title = scr.get_text(review.find('span',class_='cr-original-review-content')) if title.strip() == '' else title
                #タイトル内の「,」を「.」に変更
                title = title.replace(',','.')

                #評価は「5つ星のうち4.3」という記述のされ方なので、「ち」以降の数値のみを取得
                star = scr.get_text(review.find('span',class_='a-icon-alt'))
                star = star[star.find('ち')+1:]

                #日付けは「2022年6月16日に日本でレビュー済み」という記述のされ方なので、「に」までの文字列を取得
                date = scr.get_text(review.find('span',class_='a-size-base a-color-secondary review-date'))
                date = date[:date.find('に')]

                #レビューの内容を取得
                comment = scr.get_text(review.find('span',class_='a-size-base review-text review-text-content'))
                #コメント内の「,」を「.」に変更
                comment = comment.replace(',','.')

                #CSV出力用のDFに登録
                scr.add_df([str(row['POS_ID']),row['Item'],"Amazon",date,star,title,comment],['pos_id','item','site_name','review_date','star','title','comment'],['\n'])
                #print(data_df)

            #ページ内のレビュー数が１０未満なら最後と判断してループを抜ける
            if len(reviews) < 10:
                break
    #コメントが重複するレコードを削除する
    scr=scr.drop_duplicates(subset=['pos_id', 'site_name', 'review_date', 'comment'])
    #スクレイプ結果をCSVに出力
    return scr
