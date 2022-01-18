from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import requests
import time


def parse_flats():
    client = MongoClient('127.0.0.1', 27017)
    db = client['flats_vl']
    db.flats.delete_many({'living_complex_name': 'ЖК Эко Сити'})
    urls = ['https://жкэкосити.рф/interactive/?complex=jeko-siti&building=690', 
            'https://жкэкосити.рф/interactive/?complex=jeko-siti&building=685', 
            'https://жкэкосити.рф/interactive/?complex=jeko-siti&building=321']
    service = Service(os.path.dirname(__file__) + '/geckodriver')
    options = Options()
    options.add_argument('--window-size=1200, 800')
    options.headless = True
    driver = Firefox(options=options, service=service)
    for url in range(len(urls)):
        driver.get(urls[url])
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(5)
        q_ty = driver.find_element(By.CLASS_NAME, 'a-filter-tech__count-search')
        types = driver.find_elements(By.CLASS_NAME, 'a-table-komn')
        drawings = driver.find_elements(By.XPATH, '//div[@class="a-table-img"]/img')
        numbers = driver.find_elements(By.CLASS_NAME, 'a-table-num')
        floors = driver.find_elements(By.CLASS_NAME, 'a-table-etazh')
        sq = driver.find_elements(By.CLASS_NAME, 'a-table-pl')
        prices = driver.find_elements(By.CLASS_NAME, 'a-table-price')
        print(q_ty.text)
        print('els= ', len(types))
        for i in range(len(types)):
            db_item = {}
            if url == 0:
                db_item['num_dom'] = 3
            elif url == 1:
                db_item['num_dom'] = 2
            else:
               db_item['num_dom'] = 1
            db_item['num_fl'] = int(numbers[i].text[1:])
            db_item['_id'] = int(f'3{db_item["num_dom"]}{db_item["num_fl"]}')
            db_item['living_complex_name'] = "ЖК Эко Сити"
            db_item['flat_type'] = types[i].text.split()[0]
            db_item['floor'] = int(floors[i].text)
            db_item['planning_url'] = drawings[i].get_attribute('src')
            db_item['price'] = int(prices[i].text.split()[0].replace(',', ''))
            db_item['flat_sq'] = float(sq[i].text.split()[0])
            db_item['flat_decor'] = 'Нет'
            os.makedirs(f'{os.path.dirname(__file__)}/images/ecocity/{db_item["num_dom"]}/', exist_ok=True)
            filename = f'{os.path.dirname(__file__)}/images/ecocity/{db_item["num_dom"]}/{db_item["planning_url"].split("/")[-1].replace("@", ".")}'
            db_item['path_to_planning'] = filename
            if os.path.exists(filename):
                os.remove(filename)
            r = requests.get(db_item["planning_url"])
            with open(filename, 'wb') as f:
                f.write(r.content)
            db.flats.insert_one(db_item)     
    driver.close()



parse_flats()
                
