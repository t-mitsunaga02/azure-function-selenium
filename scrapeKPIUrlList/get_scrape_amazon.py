import logging
from .classfile import Scrape

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from urllib.parse import urlparse

#スクレイピングの関数を定義する
def get_scrape_kakaku(url):
    scr = Scrape(wait=2,max=5)
 
    #レビューのURLから商品IDの手前までを取り出す
    url = url[:url.find('#tab')]
 
    for n in range(1,1000):
        #商品の指定ページのURLを生成
        target = url+f'?Page={n}#tab'
        print(f'get：{target}')
        logging.info(f'get：{target}')
 
        #レビューページの取得
        soup = scr.request(target)

        foundForDesc = soup.find('meta', attrs={'name': 'keywords'})
        content = foundForDesc.get("content")
        maininfo = content.split(',')
        product = maininfo[0]              
        maker = maininfo[1]
        print(product)

        #ページ内のレビュー記事を一括取得
        reviews = soup.find_all('div',class_='revMainClmWrap')
        #ページ内のすべてと評価を一括取得
        evals = soup.find_all('div',class_='reviewBoxWtInner')
        
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
            ths = tables[1].find_all('th')
            tds = tables[1].find_all('td')
 
            columns = ['maker','product','date','title','comment','満足度']
            values = [maker,product,date,title,comment,star] 
 
            for th,td in zip(ths,tds):
                columns.append(th.text)
                values.append(td.text)
            
            #DataFrameに登録
            scr.add_df(values,columns,['<br>'])
        
        #ページ内のレビュー数が15未満なら、最後のページと判断してループを抜ける
        if len(reviews) < 15:
            break
    #スクレイプ結果をCSVに出力
    return scr
