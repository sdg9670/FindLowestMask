from bs4 import BeautifulSoup
import requests


def main():
    response = requests.get('http://browse.gmarket.co.kr/search?keyword=kf94+%EB%A7%88%EC%8A%A4%ED%81%AC&s=3&k=0&p=1')
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find(attrs={'class': 'section__module-wrap', 'module-design-id': '15'})
    items = table.find_all('div', attrs={'class': ['box__component box__component-itemcard '
                                                   'box__component-itemcard--general',
                                                   'box__component box__component-itemcard '
                                                   'box__component-itemcard--smiledelivery'
                                                   ]})

    result = list()

    for i, v in enumerate(items):
        items[i] = v.find('div', attrs={'class': 'box__item-container'}).find('div',
                                                                              attrs={'class': 'box__information'})
        item = dict()
        tmp = items[i].find('div', attrs={'class': 'box__item-title'})
        item['title'] = tmp.find('span', attrs={'class': 'text__item'})['title']
        item['link'] = tmp.find('a', attrs={'class': 'link__item'})['href']
        item['price'] = int(items[i].find('div', attrs={'class': 'box__item-price'}).find(attrs={'class': 'text text__value'}).text.replace(',',''))
        result.append(item)

    print(result)
    print(len(result))


main();
