
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import requests
from bs4 import BeautifulSoup
import random
import datetime
import time
import pandas as pd
import unicodedata

#新しいクラス（モジュール）を作る 
class Scrape():
 
    def __init__(self,wait=1,max=None):
        self.response = None
        self.df = pd.DataFrame()
        self.wait = wait
        self.max = max
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
        self.timeout = 5

    def get_driver(self):
        '''
        ## seleniumにてブラウザ操作するための準備
        return :
            Chrome接続情報        
        '''
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        ## Dockerにあるchromedriverを使用
        service = Service(executable_path=r"/usr/local/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)

    def request(self,url,wait=None,max=None,console=True):
        '''
        指定したURLからページを取得する。
        取得後にwaitで指定された秒数だけ待機する。
        max が指定された場合、waitが最小値、maxが最大値の間でランダムに待機する。

        Params
        ---------------------
        url:str
            URL
        wait:int
            ウェイト秒
        max:int
            ウェイト秒の最大値
        console:bool
            状況をコンソール出力するか
        Returns
        ---------------------
        soup:BeautifulSoupの戻り値
        '''
        self.wait = self.wait if wait is None else wait
        self.max = self.max if max is None else max

        start = time.time()
        response = requests.get(url,headers=self.headers,timeout = self.timeout)
        time.sleep(random.randint(self.wait,self.wait if self.max is None else self.max))

        if console:
            tm = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            lap = time.time() - start
            print(f'{tm} : {url}  経過時間 : {lap:.3f} 秒')

        return BeautifulSoup(response.content, "html.parser")

    def to_csv(self,filename,dropcolumns=None):
        '''
        DataFrame をCSVとして出力する
        dropcolumns に削除したい列をリストで指定可能
 
        Params
        ---------------------      
        filename:str
            ファイル名
        dropcolumns:[str]
            削除したい列名            
        '''
        if dropcolumns is not None:
            self.df.drop(dropcolumns,axis=1,inplace=True) 
        self.df.to_csv(filename,index=False,encoding="shift-jis",errors="ignore")

    def add_df(self,values,columns,omits = None):
        '''
        指定した値を　DataFrame に行として追加する
        omits に削除したい文字列をリストで指定可能
 
        Params
        ---------------------      
        values:[str]
            列名
        omits:[str]
            削除したい文字、又は文字列            
        '''
        if omits is not None:
            values = self.omit_char(values,omits)
            columns = self.omit_char(columns,omits)
        
        df = pd.DataFrame(values,index=self.rename_column(columns))
        self.df = pd.concat([self.df,df.T])

    def omit_char(self,values,omits):
        '''
        リストで指定した文字、又は文字列を削除する
 
        Params
        ---------------------      
        values:str
            対象文字列
        omits:str
            削除したい文字、又は文字列            
 
        Returns
        ---------------------
        return :str
            不要な文字を削除した文字列
        '''
        for n in range(len(values)):
            for omit in omits:
                values[n] = values[n].replace(omit,'')
        return values

    def rename_column(self,columns):
        '''
        重複するカラム名の末尾に連番を付与し、ユニークなカラム名にする
            例 ['A','B','B',B'] → ['A','B','B_1','B_2']
 
        Params
        ---------------------      
        columns: [str]
            カラム名のリスト
          
        Returns
        ---------------------
        return :str
            重複するカラム名の末尾に連番が付与されたリスト
        '''
        lst = list(set(columns))
        for column in columns:
            dupl = columns.count(column)
            if dupl > 1:
                cnt = 0
                for n in range(0,len(columns)):
                    if columns[n] == column:
                        if cnt > 0:
                            columns[n] = f'{column}_{cnt}'
                        cnt += 1
        return columns
    
    def normalize_string(self,input_str):
        # 文字列を小文字に変換
        lower_str = input_str.lower()
        
        # 全角文字を半角文字に変換
        half_width_str = unicodedata.normalize('NFKC', lower_str)
        
        # スペースを削除
        no_space_str = half_width_str.replace(" ", "")
        
        return no_space_str
