import logging
from .classfile import Scrape

from selenium.webdriver.common.by import By
import time
import re
from urllib.parse import urlparse

def get_url_amazon(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=2,max=5)

    # 2.各サイトURL検索
    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        # Amazon検索
        ## Amazonの検索ページを表示する
        target = f"https://www.amazon.co.jp/s?k={row['BRAND']}+{row['Item']}&crid=3M1NNK3XMSY5M&sprefix=kc-n50%2Caps%2C174&ref=nb_sb_noss_1"

        scr = Scrape(wait=2,max=5)
        soup = scr.request(target)

        ## 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(3)

        ## 製品ページのタグを取得
        shop_url = soup.find_all('a',class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')

        ## asinの初期化
        asin_url = ""

        ## 検索結果を１つずつみて、該当の製品ID（asin）を取得するループ
        for link in shop_url:
            ### 製品のタイトルを取得
            link_text = link.find('span', class_='a-size-base-plus a-color-base a-text-normal')
            
            logging.info("タイトル:")
            logging.info(link_text)

            if link_text:
                logging.info("タイトルあり:")
                logging.info(link_text)
                ### 検索した製品と同名かどうか
                if row['Item'] not in link_text.text: 
                    continue
                ### フィルタ製品じゃないかどうか
                if "フィルタ" in link_text.text:
                    continue

                ### 製品ページのURLからasinIDを取得
                asin_url = link.get('href')
                logging.info("asin取得:")
                logging.info(asin_url)

                match = re.search(r'/dp/(\w{10})', asin_url)
                asin_string = match.group(1)
                print(asin_string)

                #DataFrameに登録
                columns = ['ID','BRAND','Item','asinID']
                values = [row['ID'],row['BRAND'],row['Item'],asin_string] 
                scr.add_df(values,columns)

            else:
                continue

        ## 製品ページへ遷移
        driver = scr.get_driver()
        driver.get(f"https://www.amazon.co.jp{asin_url}")

        ## 色・スタイルの切り替えのためリンクを取得
        li_elements = driver.find_elements(By.CSS_SELECTOR, "li[data-csa-c-content-id='twister-desktop-configurator-swatch-swatchAvailable']")

        logging.info("asin_url:")
        logging.info(asin_url)

        ## 色・スタイルのリンク分ループ
        for li in li_elements:
            ### リンクの押下
            submit_button = li.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_button.click()

            ### 新しいページがロードされるのを待機
            time.sleep(3)

            ### 切り替え後の製品タイトル取得
            color_text = driver.find_element(By.CSS_SELECTOR, "span.a-size-large.product-title-word-break")
            print(f"color:{color_text.text}")

            ### 切り替え後のタイトルが検索した製品と同名かどうか
            if row['Item'] not in color_text.text: 
                continue
            ### 切り替え後のタイトルがフィルタ製品じゃないかどうか
            if "フィルタ" in color_text.text:
                continue

            ### 製品ページのURLからasinIDを取得
            match = re.search(r'/dp/(\w{10})', driver.current_url)
            asin_string = match.group(1)

            print(f"mojiretu:{asin_string}")

            #DataFrameに登録
            columns = ['ID','BRAND','Item','asinID']
            values = [row['ID'],row['BRAND'],row['Item'],asin_string] 
            scr.add_df(values,columns)
            scr.df.drop_duplicates()
        driver.quit()
    return scr
