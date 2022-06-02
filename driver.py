from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json
from bs4 import BeautifulSoup

options = Options()

options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/98.0.4758.141 YaBrowser/22.3.2.644 Yowser/2.5 Safari/537.36")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")

url = "https://linkmark.ru/"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def write(exit_file, filename):
    exit_file = json.dumps(exit_file)
    exit_file = json.loads(str(exit_file))
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(exit_file, file, indent=3, ensure_ascii=False)


class Item:
    def __init__(self, certificate=None, start_date=None, end_date=None, mktu=None, owner=None, status=None,
                 source=None, image=None):
        self.certificate = certificate
        self.start_date = start_date
        self.end_date = end_date
        self.mktu = mktu
        self.owner = owner
        self.status = status
        self.source = source
        self.image = image


def start_driver(search_item):
    try:
        data = {
            "items": []
        }

        driver.get(url=url)
        time.sleep(1)

        search_input = driver.find_element_by_class_name("search-input")
        search_input.clear()
        search_input.send_keys(search_item)
        time.sleep(0.5)

        driver.find_element_by_id("search-bottom").click()
        time.sleep(5)

        response = requests.get(driver.current_url)
        soup = BeautifulSoup(response.text, 'lxml')
        blocks = soup.find_all('div', {"class": "result-div-item"})

        for block in blocks:

            trList = block.findAll('tr')
            mass = [None, None, None, None, None]

            for tr in trList:
                tr = tr.find('th')
                try:
                    if "Свидетельство" in tr.get_text(strip=True):
                        mass[0] = tr.next_sibling.get_text(strip=True)
                except Exception as ex:
                    print(ex)

                try:
                    if "Приоритет:" in tr.get_text(strip=True):
                        mass[1] = tr.find_next("td").get_text(strip=True)

                except Exception as ex:
                    print(ex)

                try:
                    if "Дата регистрации:" in tr.get_text(strip=True):
                        mass[2] = tr.find_next("td").get_text(strip=True)

                except Exception as ex:
                    print(ex)

                try:
                    if "МКТУ" in tr.get_text(strip=True):
                        mass[3] = tr.next_sibling.get_text(strip=True)
                except Exception:
                    pass

                try:
                    if "Правообладатель" in tr.get_text(strip=True):
                        mass[4] = tr.next_sibling.get_text(strip=True)
                except Exception:
                    pass

            if mass[0] is None and mass[1] is None and mass[2] is None and mass[3] is None and mass[4] is None:
                try:
                    mass[0] = block.find('div', class_="result-div-item-number").get_text(strip=True)

                except Exception as ex:
                    print(ex)

                try:
                    mass[3] = block.find('div', class_="result-div-item-mktu").get_text(strip=True)

                except Exception as ex:
                    print(ex)

                try:
                    mass[4] = block.find('div', class_="result-div-item-owner").get_text(strip=True)

                except Exception as ex:
                    print(ex)

            item = Item(None)
            item.certificate = mass[0]
            item.start_date = mass[1]
            item.end_date = mass[2]
            item.mktu = mass[3]
            item.owner = mass[4]

            try:
                item.status = block.find('div', class_="result-div-item-status tm_status status_2").get_text(strip=True)

            except Exception:

                try:
                    item.status = block.find('div', class_="result-div-item-status tm_status status_1").get_text(
                        strip=True)
                except Exception:
                    item.status = None

            try:
                item.source = block.find('div', class_="result-div-item-action").find('a').get('href')

            except Exception:
                item.source = None

            try:
                item.image = block.find('div', class_="result-div-item-image").find('img').get('src')

            except Exception:
                item.image = None

            data['items'].append(item.__dict__)
            # write(data, "data.json")
        return data

    except Exception as ex:
        print(ex)
        driver.close()
        driver.quit()
        return False

