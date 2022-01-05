from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from lxml import html
import requests
from pprint import pprint
import os
import datetime
import re


def get_urls():
    url_links = []
    url = 'https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?objStatus=0&objectIds=40147%2C36755%2C38743&residentialBuildings=1&place=0-26&page=0&limit=100'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        dom = html.fromstring(res.text)
        p = dom.xpath('//a[@class="pagination-item"]/text()')
    
        for i in range(int(p[-1])):
            u = f'https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?objStatus=0&objectIds=40147%2C36755%2C38743&residentialBuildings=1&place=0-26&page={i}&limit=100'
            res = requests.get(u, headers=headers)
            if res.status_code == 200:
                dom = html.fromstring(res.text)
                objs = dom.xpath('//a[contains(@class, "styles__Address-sc-")]/@href')
                pprint(objs)
                for item in objs:
                    url_links.append('https://наш.дом.рф/сервисы/каталог-новостроек/объект/' + item.split('/')[-1])

    return url_links


def parse_object(url):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    res = requests.get(url, headers=header)
    if res.status_code == 200:
        dom = html.fromstring(res.text)
        dom_id = dom.xpath('//p[contains(@class, "styles__Id-sc-")]/text()')[0].split(':')[-1]
        print(f'ID дома: {dom_id}')
        name = dom.xpath('//h1/text()')[0]
        print(f'название ЖК: {name}')
        addr = dom.xpath('//p[contains(@class, "styles__Address-sc-eng632-11")]/text()')
        print(addr[1])
        owner = dom.xpath('//a[contains(@class, "styles__LinkContainer-sc-1u7ca6h-0")]/text()')[0]
        print(f'застройщик: {owner}')
        try:
            building_company = dom.xpath('//div[contains(@class, "styles__Wrapper-sc-uaqryz-0")]/text()')
            print(building_company[1])
        except Exception:
            print('Генподрядчики: не указаны')
        pr_declaration_text = dom.xpath('//div[contains(@class, "styles__Decl-sc-kydjcf-0")]/text()')[1:]
        print(f'проектная декларация: {" ".join(pr_declaration_text)}')
        pr_declaration_link = dom.xpath('//a[contains(@class, "styles__DownloadLink-sc-1fv64wt-0")]/@href')[0]
        print(f'ссылка на проектную декларацию: {pr_declaration_link}')
        others_ch = dom.xpath('//div[contains(@class, "styles__Value-sc-13pfgqd-2")]/text()')
        # print('others_ch_len = ', len(others_ch))
        # print(others_ch)
        if len(others_ch) == 5:
            print(f'срок сдачи: {" ".join(others_ch[0:2])}')
            print(f'выдача ключей: {others_ch[2]}')
            print(f'средняя цена 1 м2: {others_ch[-2]} руб.') 
        else:
            print(f'срок сдачи: {" ".join(others_ch[0:2])}')
            print(f'выдача ключей: {others_ch[2]}')
            print(f'средняя цена 1 м2: {int("".join(others_ch[3].split()))} руб.')
        main_features = dom.xpath('//span[contains(@class, "styles__RowSpan-sc-1fyyfia-7")]/text()')
        imgs = dom.xpath('//div[contains(@class, "swiper-slide")]/img/@src')
        for img in imgs:
            print(f'ссылка фото ЖК: {img}')
        print(f'класс недвижимости: {main_features[1]}')
        print(f'материал стен: {main_features[3]}')
        print(f'тип отделки: {main_features[5]}')
        print(f'свободная планировка: {main_features[7]}')
        print(f'кол-во этажей: {main_features[9]}')
        print(f'кол-во квартир: {main_features[11]}')
        print(f'жилая площадь: {main_features[13]} м2')
        print(f'высота потолков: {main_features[15]} м')
        l = dom.xpath('//a[contains(@class, "styles__Message-sc-1f4oj2n-1")]/@href')[0]
        res = requests.get(l, headers=header)
        if res.status_code == 200:
            dom = html.fromstring(res.text)
            rows = dom.xpath('//div[contains(@class, "styles__Row-sc-tefync-3")]')
            print('Перенос плановых сроков строительства')
            for row in range(len(rows)):
                if row > 4:
                    break
                ds = rows[row].xpath('.//div/text()')
                print(f"{ds[0]} {ds[1]} {ds[2]} {' '.join(el for el in ds[3:] if el != ' ')}") 
            print('Перенос сроков передачи квартир гражданам – участникам долевого строительства')
            rs = dom.xpath('//div[contains(@class, "styles__Cell-sc")]/text()')
            rs_text = dom.xpath('//span[contains(@class, "styles__")]/text()')
            print(f'{rs[6]} {rs[7]} {"".join(el for el in rs_text[0:3] if el != " ")}')


def parse_flats():
    url_links = get_urls()
    for link in url_links:
        parse_object(link)
        print('-'*50)


parse_flats()




