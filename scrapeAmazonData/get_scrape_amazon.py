import logging
from .class_file import Scrape
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os
import datetime
import time

def get_scrape_amazon(url_data):
    scr = Scrape(wait=2,max=5)
    # エラー出力用に実行中のファイル名を取得する
    file_path = os.path.abspath(__file__)
    file_name = os.path.basename(file_path)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        #最大500ページ分（500×10=5000レビュー分）を読み出すループ
        for n in range(1,500):
            #商品IDからレビュー記事のページを生成
            target = f"https://www.amazon.co.jp/product-reviews/{row['asinID']}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&formatType=current_format&pageNumber={n}#reviews-filter-bar"

            # Selenium 設定
            driver = scr.get_driver()
            driver.get(target)
            print(f"ページ遷移：{target}")
            logging.info(f"ページ遷移：{target}")

            time.sleep(5)
            logging.info(f"get：{driver.current_url}")

            #ページ内のレビューを全て取得(1ページ10レビュー)
            reviews = driver.find_elements(By.XPATH, "//*")

            # reviews = driver.find_elements(By.CSS_SELECTOR, 'div.a-section.review.aok-relative')
            print(f'ページ数:{n}')
            print(f'レビュー数:{len(reviews)}')
            logging.info(f'ページ数:{n}')
            logging.info(f'レビュー数:{len(reviews)}')
            for element in reviews:
                logging.info(f"テキスト:{element.tag_name}, {element.text}")

            #レビューの数だけループ
            for review in reviews:
                #日本のレビューアが書いたレビューのタイトルを取得
                try:
                    title = review.find_element(By.CSS_SELECTOR, 'a.a-size-base.a-link-normal.review-title.a-color-base.review-title-content.a-text-bold')
                  
                    #タイトル内の「,」を「.」に変更
                    title_text = title.text.replace(',','.')

                    #評価は「5つ星のうち4.3」という記述のされ方なので、「ち」以降の数値のみを取得
                    star = review.find_element(By.TAG_NAME, "i")
                    star_span = star.find_element(By.XPATH, ".//span[@class='a-icon-alt']")
                    span_text = star_span.get_attribute('innerHTML')
                    star_text = span_text[span_text.find('ち')+1:]

                    #日付けは「2022年6月16日に日本でレビュー済み」という記述のされ方なので、「に」までの文字列を取得
                    date = review.find_element(By.CSS_SELECTOR, 'span.a-size-base.a-color-secondary.review-date')
                    date_text = date.text
                    date = date_text[:date_text.find('に')]

                    #レビューの内容を取得
                    comment = review.find_element(By.CSS_SELECTOR, 'span.a-size-base.review-text.review-text-content')
                    #コメント内の「,」を「.」に変更
                    comment = comment.text.replace(',','.')

                except NoSuchElementException as e:
                    # エラー内容を出力し、処理を抜ける
                    print(f"Amazon,{row['Item']},{datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')},{file_name},{e}")
                    continue   

                #CSV出力用のDFに登録
                scr.add_df([str(row['POS_ID']),row['Item'],"Amazon",date,star_text,title_text,comment],['pos_id','item','site_name','review_date','star','title','comment'],['\n'])

            #ページ内のレビュー数が１０未満なら最後と判断してループを抜ける
            if len(reviews) < 10:
                break

    #コメントが重複するレコードを削除する
    scr = scr.df.drop_duplicates(subset=['pos_id', 'site_name', 'review_date', 'comment'])
    #スクレイプ結果をCSVに出力
    return scr
