from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import os
import datetime
import time


def parse_flats():
    data = datetime.datetime.now().strftime('%d.%m.%Y_%H:%M')
    path = os.path.join(os.path.dirname(__file__), f'{data}_ecocity_flats.txt')
    urls = ['https://жкэкосити.рф/interactive/?complex=jeko-siti&building=321', 'https://жкэкосити.рф/interactive/?complex=jeko-siti&building=685', 'https://жкэкосити.рф/interactive/?complex=jeko-siti&building=690']
    s = Service(os.path.dirname(__file__) + '/geckodriver')
    driver = Firefox(service=s)
    with open(path, 'w', encoding='utf-8') as f:
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
            drs = driver.find_elements(By.CLASS_NAME, 'a-table-img')
            numbers = driver.find_elements(By.CLASS_NAME, 'a-table-num')
            floors = driver.find_elements(By.CLASS_NAME, 'a-table-etazh')
            sq = driver.find_elements(By.CLASS_NAME, 'a-table-pl')
            prices = driver.find_elements(By.CLASS_NAME, 'a-table-price')
            # print(q_ty.text)
            f.write(f'{q_ty.text}\n\n')
            for i in range(len(types)):
                f.write(f'№: {i+1}\n')
                if url == 0:
                    # print('Адрес: Дом №1')
                    f.write('Адрес: Дом №1\n')
                elif url == 1:
                    # print('Адрес: Дом №2')
                    f.write('Адрес: Дом №2\n')
                else:
                    # print('Адрес: Дом №3')
                    f.write('Адрес: Дом №3\n')
                # print(f'Номер квартиры: {numbers[i].text}')
                f.write(f'Номер квартиры: {numbers[i].text}\n')
                # print(f'Этаж: {floors[i].text}')
                f.write(f'Этаж: {floors[i].text}\n')
                # print(f'Тип квартиры: {types[i].text}')
                f.write(f'Тип квартиры: {types[i].text}\n')
                # print(f'Площадь: {sq[i].text}')
                f.write(f'Площадь: {sq[i].text}\n')
                # print(f'Стоимость: {" ".join(prices[i].text[0:10].split(","))} руб.')
                f.write(f'Стоимость: {" ".join(prices[i].text[0:10].split(","))} руб.\n')
                f.write(f'Планировка: {drs[i].find_element(By.TAG_NAME, "img").get_attribute("src")}\n')
                # print(f'Планировка: {drs[i].find_element(By.TAG_NAME, "img").get_attribute("src")}')
                # print('-'*50)
                f.write('-------------------------------------------\n')
                
            f.write('\n*******************************************\n\n')
    driver.close()


parse_flats()
          
