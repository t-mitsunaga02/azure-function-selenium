import logging
from .classfile import Scrape

from selenium.webdriver.common.by import By
import time
import re
from urllib.parse import urlparse

def get_url_amazon(get_pos):
    # クラスファイルの呼び出し
    scr = Scrape(wait=5,max=5)

    # 2.各サイトURL検索
    ## メーカー・製品毎にサイト検索するループ
    for index, row in get_pos.iterrows():

        ## メーカー・製品名の抽出
        search_word = f"{row['BRAND']} {row['Item']}"

        # Amazon検索
        ## Amazonの検索ページを表示する
        target = f"https://www.amazon.co.jp/s?k={row['BRAND']}+{row['Item']}&crid=3M1NNK3XMSY5M&sprefix=kc-n50%2Caps%2C174&ref=nb_sb_noss_1"
        logging.info(f"製品開始：{target}")
        soup = scr.request(target)

        ## 検索結果ページがロードされるのを待つ（例: 3秒待つ）
        time.sleep(5)

        ## 製品ページのタグを取得
        shop_url = soup.find_all('a',class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
        logging.info(f"製品タイトル数：{len(shop_url)}")

        ## 検索結果を１つずつみて、該当の製品ID（asin）を取得するループ
        for link in shop_url:
            ### 製品のタイトルを取得
            link_text = link.find('span', class_='a-size-base-plus a-color-base a-text-normal')
            if link_text:
                logging.info(f"製品名：{scr.normalize_string(row['Item'])}")
                ### 検索した製品と同名かどうか
                if scr.normalize_string(row['Item']) not in scr.normalize_string(link_text.text): 
                    continue
                ### フィルタ製品じゃないかどうか
                if "フィルタ" in link_text.text:
                    continue
                logging.info(f"製品タイトル：{scr.normalize_string(link_text.text)}")
                ### 製品ページのURLからasinIDを取得
                asin_url = link.get('href')
                match = re.search(r'/dp/(\w{10})', asin_url)
                asin_string = match.group(1)
                print(f"製品ID：{asin_string}")
                logging.info(f"製品ID：{asin_string}")

                ### DataFrameに登録
                columns = ['ID','BRAND','Item','asinID']
                values = [row['ID'],row['BRAND'],row['Item'],asin_string]  
                scr.add_df(values,columns)
                logging.info(scr.df.head())

                ### 色/スタイルなどの違いがある製品を取得
                color_target = f"https://www.amazon.co.jp{asin_url}"
                color_soup = scr.request(color_target)
                time.sleep(5)

                ### エレメントが3種類切り替わるため
                color_url_1 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare')
                color_url_2 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal dimension-values-list')
                color_url_3 = color_soup.find_all('ul', class_='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches')

                color_url = color_url_1 + color_url_2 + color_url_3

                print(f"数:{len(color_url)}")
                ### 色違い製品がない場合はループを抜ける
                if not color_url :
                    continue

                ### リンク切り替えループ
                for urls in color_url:
                    ### asinID取得
                    pattern = r"data-csa-c-item-id=.{1}(.{10})"
                    hits = re.findall(pattern, str(urls))
                    ### asinID毎に遷移するループ
                    for asin in hits:
                        logging.info(f"色違い製品asin：{asin}")
                        print(asin)
                        ### asinIDを置換し遷移する
                        replace_asin = f"/dp/{asin}"
                        re_asin_url = re.sub(r'/dp/(\w{10})', replace_asin, color_target)
                        print(re_asin_url)
                        re_asin_soup = scr.request(re_asin_url)
                        time.sleep(5)

                        re_asin_text = re_asin_soup.find('span', class_='a-size-large product-title-word-break')

                        # print(re_asin_text.text)
                        if re_asin_text:
                            ### 検索した製品と同名かどうか
                            logging.info(f"色違いタイトル：{scr.normalize_string(re_asin_text.text)}")
                            if scr.normalize_string(row['Item']) not in scr.normalize_string(re_asin_text.text): 
                                continue
                            ### フィルタ製品じゃないかどうか
                            if "フィルタ" in re_asin_text.text:
                                continue
                            ### DataFrameに登録
                            logging.info(f"色違いasin：{asin}")
                            columns = ['ID','BRAND','Item','asinID']
                            values = [row['ID'],row['BRAND'],row['Item'],asin] 
                            scr.add_df(values,columns)
                            scr.df.drop_duplicates()
                            logging.info(scr.df.head())
                        else:
                            continue
            
            else:
                continue
    return scr
