#!/usr/bin/python3

import csv
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

wards = { 
    '東区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/005higashi.html',
    '博多区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/007hakata.html',
    '中央区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/004chuo.html', 
    '南区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/006minami.html', 
    '城南区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/jonan.html', 
    '早良区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/003sawara.html', 
    '西区':	'https://www.city.fukuoka.lg.jp/kankyo/kateigomi/life/002nishi.html',
    }


with open("area_days.csv", "w", encoding='utf-8') as file:
    fieldnames = [ '地名', 'センター', '燃えるごみ', '燃えないごみ', '空きびん・ペットボトル' ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    
    for wardName, wardUrl in wards.items():
    
        # URLの指定
        html = urlopen(wardUrl)
        bsObj = BeautifulSoup(html, "html.parser")
        
        # テーブルを指定
        table = bsObj.findAll("table")[0]
        rows = table.findAll("tr")
    
        rowspanCount = { 'gojuuon':0, 'choumei':0, 'bangou':0, 'moerugomi':0, 'moenaigomi':0, 'akibinpet':0 }
        rowspanContents = { 'gojuuon':"", 'choumei':"", 'bangou':"", 'moerugomi':"", 'moenaigomi':"", 'akibinpet':"" }
        columnContents = { 'gojuuon':"", 'choumei':"", 'bangou':"", 'moerugomi':"", 'moenaigomi':"", 'akibinpet':"" }
    
        for row in rows:
            csvRow = []
            i = 0
            try:
                _ = row.findAll(['td'])
                for column in ['gojuuon', 'choumei', 'bangou', 'moerugomi', 'moenaigomi', 'akibinpet' ]:
                    if rowspanCount[column] > 0:
                        columnContents[column] = rowspanContents[column]
                        rowspanCount[column] -= 1
                    else:
                        columnContents[column] = _[i].get_text()
                        try:
                            rowspanCount[column] = int(_[i]['rowspan'])-1
                            rowspanContents[column] = _[i].get_text()
                        except KeyError:
                            pass
                        i += 1
    
                if not re.match(r'毎週.曜日', columnContents['moerugomi']):
                    columnContents['moerugomi'] = re.sub(r'(.)曜日・(.)曜日', r'\1 \2', columnContents['moerugomi'])
                else: # 早良区大字板屋のみのはず
                    columnContents['moerugomi'] = re.sub(r'毎週(.)曜日', r'\1', columnContents['moerugomi'])
    
                writer.writerow({
                    '地名': wardName + ' ' + (columnContents['choumei']+columnContents['bangou']).translate(str.maketrans({' ': None, '　': None, ',': '，'})),
                    'センター': '', 
                    '燃えるごみ': columnContents['moerugomi'], 
                    '燃えないごみ': re.sub(r'(.)回目の(.)曜日', r'\2\1', columnContents['moenaigomi'].translate(str.maketrans('０１２３４５６７８９', '0123456789'))), 
                    '空きびん・ペットボトル': re.sub(r'(.)回目の(.)曜日', r'\2\1', columnContents['akibinpet'].translate(str.maketrans('０１２３４５６７８９', '0123456789')))
                    })

            except IndexError:
                pass

# 参考にしたサイト
# 【Python】BeautifulSoupを使ってテーブルをスクレイピング
# https://qiita.com/hujuu/items/b0339404b8b0460087f9
