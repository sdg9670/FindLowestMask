from bs4 import BeautifulSoup
from time import sleep
import requests
from openpyxl import Workbook
from datetime import datetime
from urllib import parse

keywords = ['kf94 마스크', 'kn95 마스크', 'pm2.5 마스크']
filters = ['필터', '정전기', '교체', 'BFE', 'bfe', '고리', '입체', '연예인', '거치대', '유아', '어린이', '위생', '아동']
maxPrice = 2000

def getGMarket():
    result = list()
    for keyword in keywords:
        for pageNum in range(1, 100):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.139 Safari/537.36'}
            response = requests.get(
                'http://browse.gmarket.co.kr/search?keyword=' + parse.quote_plus(keyword) + '&s=3&k=0&p=' + str(pageNum),
                headers=headers
            )

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find(attrs={'class': 'section__module-wrap', 'module-design-id': '15'})

            try:
                items = table.find_all('div', attrs={'class': ['box__component box__component-itemcard '
                                                               'box__component-itemcard--general',
                                                               'box__component box__component-itemcard '
                                                               'box__component-itemcard--smiledelivery'
                                                               ]})
            except Exception:
                break

            for i, v in enumerate(items):
                items[i] = v.find('div', attrs={'class': 'box__item-container'}).find('div',
                                                                                      attrs={'class': 'box__information'})
                item = dict()
                tmp = items[i].find('div', attrs={'class': 'box__item-title'})
                item['title'] = tmp.find('span', attrs={'class': 'text__item'})['title']

                filterCheck = False
                for f in filters:
                    if item['title'].find(f) != -1:
                        filterCheck = True
                        break

                if filterCheck:
                    continue


                item['link'] = tmp.find('a', attrs={'class': 'link__item'})['href']
                item['price'] = int(items[i].find('div', attrs={'class': 'box__item-price'})
                                    .find(attrs={'class': 'box__price-seller'})
                                    .find(attrs={'class': 'text text__value'}).text.replace(',', ''))

                tmp = item['title'].strip()
                mae = tmp.find('매') - 1
                gae = tmp.find('개') - 1
                if mae != -1:
                    item['amount'] = findAmount(tmp, mae)
                elif gae != -1:
                    item['amount'] = findAmount(tmp, gae)
                else:
                    item['amount'] = 1

                item['price'] /= item['amount']

                if item['price'] > maxPrice:
                    continue

                result.append(item)
            sleep(1)
    return result


def findAmount(string, lastNumberIndex):
    num = list()
    for i in range(lastNumberIndex, -1, -1):
        if ord('0') <= ord(string[i]) <= ord('9'):
            num.append(string[i])
        else:
            break
    if len(num) > 0:
        num.reverse()
        return int(''.join(num))
    return 1

masks = list()
masks.extend(getGMarket())
masks.sort(key=lambda r: r['price'])

wb = Workbook()
ws = wb.active

ws.column_dimensions['A'].width = 80
ws.column_dimensions['B'].width = 10
ws.column_dimensions['C'].width = 10
ws.column_dimensions['D'].width = 80

ws.append(['제목', '가격', '묶음 갯수', '링크'])
for i in masks:
    ws.append([i['title'], i['price'], i['amount'], i['link']])

wb.save('./xlsx/' + datetime.now().strftime("%Y%m%d%H%M%S") +'_마스크.xlsx')
