from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from lxml import html
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import datetime
import wget
from PIL import Image
from pprint import pprint


def get_urls():
    url_links = []
    url = 'https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?objStatus=0&residentialBuildings=1&place=0-26&page=0&limit=100'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        dom = html.fromstring(res.text)
        p = dom.xpath('//a[@class="pagination-item"]/text()')
        links = dom.xpath('//a[contains(@class, "styles__Address")]/@href')
        for link in links:
            url_links.append(link)
        s = Service(os.path.dirname(__file__) + '/geckodriver')
        # options = Options()
        # options.add_argument('--window-size=1200, 800')
        # options.headless = True
        driver = Firefox(service=s)
        for i in range(1, int(p[-1])):
            link = f'https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?objStatus=0&residentialBuildings=1&place=0-26&page={i}&limit=100'
            driver.get(link)
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//li/a")))
            objs = driver.find_elements(By.XPATH, '//a[contains(@class, "Address")]')
            print(len(objs))
            for item in objs:
                url_links.append(item.get_attribute('href'))  
        driver.close()
    print(len(url_links))
    return url_links


def parse_objects():
    client = MongoClient('127.0.0.1', 27017)
    db = client['nashdom_vl_db']
    main_collection = db['main_collection']
    url_links = get_urls()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    for url in url_links:
        res = requests.get(url, headers=header)
        if res.status_code == 200:
            db_item = {}
            dom = html.fromstring(res.text)
            dom_id = dom.xpath('//p[contains(@class, "styles__Id-sc-")]/text()')[0].split(':')[-1]
            db_item['_id'] = int(dom_id)
            name = dom.xpath('//h1/text()')[0]
            db_item['name'] = name
            addr = dom.xpath('//p[contains(@class, "styles__Address-sc-")]/text()')
            db_item['address'] = addr[1]
            owner = dom.xpath('//a[contains(@class, "styles__LinkContainer-sc-")]/text()')[0]
            db_item['main_contractor'] = owner
            try:
                building_company = dom.xpath('//div[contains(@class, "styles__Wrapper-sc-uaqryz")]/text()')
                db_item['builder'] = building_company[1]
            except Exception:
                db_item['builder'] = 'не указан'
            pr_declaration_text = dom.xpath('//div[contains(@class, "styles__Decl-")]/text()')[1:]
            db_item['pr_declaration'] = " ".join(pr_declaration_text)
            pr_declaration_link = dom.xpath('//a[contains(@class, "styles__DownloadLink-sc-1fv64wt-0")]/@href')[0]
            db_item['pr_decl_link'] = pr_declaration_link
            others_ch = dom.xpath('//div[contains(@class, "styles__Value-sc-")]/text()')
            if len(others_ch) == 5:
                db_item['building_term'] = " ".join(others_ch[0:2])
                try:
                    db_item['term_keys'] = datetime.datetime.strptime(others_ch[2], "%d.%m.%Y")
                except ValueError:
                    db_item['term_keys'] = others_ch[2]
                try:
                    db_item['mid_price'] = int(others_ch[-2].replace(' ', ''))
                except ValueError:
                    db_item['mid_price'] = others_ch[-2].split()
            else:
                db_item['building_term'] = " ".join(others_ch[0:2])
                try:
                    db_item['term_keys'] = datetime.datetime.strptime(others_ch[2], "%d.%m.%Y")
                except ValueError:
                    db_item['term_keys'] = others_ch[2]
                try:
                    db_item['mid_price'] = int(others_ch[3].replace(' ', ''))
                except ValueError:
                    db_item['mid_price'] = others_ch[3].split()
            main_features = dom.xpath('//span[contains(@class, "styles__RowSpan-sc-1fyyfia-7")]/text()')
            imgs = dom.xpath('//div[contains(@class, "swiper-slide")]/img/@src')
            os.makedirs(f'{os.path.dirname(__file__)}/images/{dom_id}/', exist_ok=True)
            for img in imgs:
                filename = f'{os.path.dirname(__file__)}/images/{dom_id}/{img.split("/")[-1].split("-")[0]}.jpg'
                if os.path.exists(filename):
                    os.remove(filename)
                wget.download(img, out=filename)
            # resize images
            path_to_dir = os.path.join(os.path.dirname(__file__), 'images', dom_id)
            files = os.listdir(path_to_dir)
            images = []
            for file in files:
                if file == files[0]:
                    img_1 = Image.open(os.path.join(path_to_dir, files[0]))
                    width, height = img_1.size
                    if width > 240:
                        width_ratio = round(240 / width * 100)
                        if img_1.mode == 'RGBA' or img_1.mode == 'P':
                            img_1 = img_1.convert('RGB')
                        new_img = f"{file.split('.')[0]}_small.jpg"
                        img_1.save(os.path.join(path_to_dir, new_img), quality=width_ratio)
                        db_item['small_img'] = os.path.join(path_to_dir, new_img)

                org_img = Image.open(os.path.join(path_to_dir, file))
                width, height = org_img.size
                if width > 1420:
                    width_ratio = round(1420 / width * 100)
                    if org_img.mode == 'RGBA' or org_img.mode == 'P':
                        org_img = org_img.convert('RGB')
                    # new_img = f"{file.split('.')[0]}_resized.jpg"
                    org_img.save(os.path.join(path_to_dir, file), quality=width_ratio)
                images.append(os.path.join(path_to_dir, file))
            db_item['main_photos'] = images
            db_item['main_class'] = main_features[1]
            db_item['all_material'] = main_features[3]
            db_item['wall_decor'] = main_features[5]
            db_item['planning'] = main_features[7]
            db_item['storeys'] = int(main_features[9])
            db_item['flats'] = int(main_features[11])
            db_item['living_sq'] = int(main_features[13].replace(' ', ''))
            try:
                db_item['ceil_height'] = float(main_features[15].replace(',', '.'))
            except ValueError:
                db_item['ceil_height'] = main_features[15].replace(',', '.')
            l = dom.xpath('//div[contains(@class, "styles__FunctionsRow-sc")]//a[contains(@class, "styles__Message")]/@href')[0]
            res = requests.get(l, headers=header)
            delay_res = []
            delay_keys = None
            if res.status_code == 200:
                dom = html.fromstring(res.text)
                rows = dom.xpath('//div[contains(@class, "styles__Row-sc-tefync-3")]')
                for row in range(len(rows)):
                    if row > 4:
                        break
                    ds = rows[row].xpath('.//div/text()')
                    delay_res.append(f"{ds[0]} {ds[1]} {ds[2]} {' '.join(el for el in ds[3:] if el != ' ')}")
                db_item['delay_terms'] = delay_res
                rs = dom.xpath('//div[contains(@class, "styles__Cell-sc")]/text()')
                rs_text = dom.xpath('//span[contains(@class, "styles__")]/text()')
                delay_keys = f'{rs[6]} {rs[7]} {"".join(el for el in rs_text[0:3] if el != " ")}'
                db_item['delay_keys'] = delay_keys
            try:
                main_collection.insert_one(db_item)
            except DuplicateKeyError:
                main_collection.update_one({'_id': db_item["_id"]},
                                           {'$set': {'delay_terms': delay_res, 'delay_keys': delay_keys}})
    return db


# parse_objects()

get_urls()


