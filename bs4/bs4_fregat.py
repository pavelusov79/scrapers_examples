from bs4 import BeautifulSoup
import requests
import os
import datetime


def parse_flats():
    data = datetime.datetime.now().strftime('%d.%m.%Y_%H:%M')
    path = os.path.join(os.path.dirname(__file__), f'{data}_fregat_flats.txt')
    urls = ['https://fregat2.ru/flats/nejbuta-dom-7/', 'https://fregat2.ru/flats/nejbuta-dom-6/', 'https://fregat2.ru/flats/nejbuta-dom-8/', 'https://fregat2.ru/flats/nejbuta-dom-5/']
    with open(path, 'w', encoding='utf-8') as f:
        for url in urls:
            headers = {'User-agent': 'Chrome/95.0.463'}
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'lxml')
                fl = soup.find_all('div', attrs={'class': 'homes__number'})
                links = soup.find_all('div', attrs={'class': 'homes__row'})
                for el in range(len(fl)):
                    # print(f'этаж: {fl[el].text}')
                    for i in links[el].contents:
                        if  i.name == 'a':
                            # print(i['href'])
                            url_fl = i['href']
                            headers = {'User-agent': 'Chrome/95.0.463'}
                            res = requests.get(url_fl, headers=headers)
                            if res.status_code == 200:
                                soup = BeautifulSoup(res.text, 'lxml')
                                dr = soup.find('div', attrs={'class': 'homes__image'})
                                info = soup.find('div', attrs={'class': 'homes__table'})
                                addr = soup.find('div', attrs={'class': 'html'})
                                # print(f'адрес: {addr.h1.text}')
                                # print(f'этаж: {fl[el].text}')
                                # print(f'планировка: {dr["data-src"]}')
                                # print(f'площадь: {info.table.tbody.text.split()[0]}')
                                if info:
                                    # f.write(f"{i['href']}\n")
                                    f.write(f'адрес: {addr.h1.text}\n')
                                    f.write(f'этаж: {fl[el].text}\n')
                                    f.write(f'площадь: {info.table.tbody.text.split()[0]}\n')
                                    f.write(f'кол-во комнат: {info.table.tbody.text.split()[1]}\n')
                                    f.write(f'стоимость: {" ".join(info.table.tbody.text.split()[2:-1])}\n')
                                    f.write(f'отделка: {info.table.tbody.text.split()[-1]}\n')
                                    if i['data-type'] == 'C ':
                                        # print('тип квартиры: студия')
                                        f.write('тип квартиры: студия\n')
                                    if i['data-type'] == ' 1 ':
                                        # print('тип квартиры: однокомнатная')
                                        f.write('тип квартиры: однокомнатная\n')
                                    if i['data-type'] == ' 2 ':
                                        # print('тип квартиры: двухкомнатная')
                                        f.write('тип квартиры: двухкомнатная\n')
                                    if i['data-type'] == ' 3 ':
                                        # print('тип квартиры: трехкомнатная')
                                        f.write('тип квартиры: трехкомнатная\n')
                                    f.write(f'планировка: {dr["data-src"]}\n')
                                # print(f'кол-во комнат: {info.table.tbody.text.split()[1]}')
                               
                                # print(f'стоимость: {" ".join(info.table.tbody.text.split()[2:-1])}')
                                
                                # print(f'отделка: {info.table.tbody.text.split()[-1]}')
                                
                                # print('-'*30)
                                f.write('--------------------------------------------------------\n')
                    # print('*'*50)
                    # f.write('*************************************************************\n\n')


parse_flats()