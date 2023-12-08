import logging
from .class_file import Scrape

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException #要素が見つからなかった時用
import time
from urllib.parse import urlparse

#スクレイピングの関数を定義する
def get_scrape_yahoo(url_data):
    scr = Scrape(wait=2,max=5)

    ## メーカー・製品毎にサイト検索するループ
    for index, row in url_data.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        #データ格納用のデータフレーム定義
        # df_columns=["date","star","title","comment"]
        # df = pd.DataFrame(columns=df_columns)

        # Selenium 設定
        driver = scr.get_driver()
        driver.get(row['ReviewURL'])
        print(row['ReviewURL'])
        logging.info(f"product：{row['Item']}")

        #レビューボタンクリック
        review_button = driver.find_element(By.XPATH, '//button[@data-cl-params="_cl_link:review;_cl_position:0;"]')
        review_button.click()
        time.sleep(3)

        #もっと見るボタンを表示される限りクリックし続けてレビューを全件表示させる。
        while True:
            try:
                # "もっと見る" ボタンを探す
                more_button = driver.find_element(By.XPATH, '//button[contains(@class, "style_reviewContents__moreButton__CUOHn")]')

                # ボタンをクリック
                more_button.click()
                time.sleep(1) #反映されるまで1秒待つ

            except NoSuchElementException:
                # "もっと見る" ボタンが見つからない場合はループを終了
                break

        #レビューのひとまとまりを取得
        reviews = driver.find_elements(By.CSS_SELECTOR, "div.style_reviewComment__0oh0m")

        # レビュー毎のループ
        for i in range(len(reviews) //2) :
            date = reviews[i].find_element(By.CSS_SELECTOR, "div.style_reviewComment__date__7vpOE").find_element(By.TAG_NAME, "span").text
            star = reviews[i].find_element(By.CSS_SELECTOR, "span.Review__average").text
            try:
                title = reviews[i].find_element(By.CSS_SELECTOR, "span.style_reviewComment__titleText__FeaWf").text
            except NoSuchElementException:
                title = ""
            try:
                comment = reviews[i].find_element(By.CSS_SELECTOR, "div.style_reviewComment__body__flntA").text
            except NoSuchElementException:
                comment = ""

            columns = ['pos_id','item','site_name','review_date','star','title','comment']
            values = [str(row['ID']),row['Item'],"Yahoo",date,star,title,comment] 
            
            #DataFrameに登録
            scr.add_df(values,columns,['\n'])

        # webdriverの終了
        driver.quit()

    #スクレイプ結果をCSVに出力
    return scr
