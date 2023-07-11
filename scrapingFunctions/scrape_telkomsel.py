import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

url = 'https://www.telkomsel.com/shops/digital-product/package?utm_source=wec&utm_medium=quickbutton&utm_campaign=belipaket&utm_id=wec-isipaket&msisdn=&type=internet&category=Semua%20Paket&roaming=&service=PraBayar&sort=&minPrice=&maxPrice=&quota='

def scrape_data(url) :
    driver = webdriver.Chrome()
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    list_products = []
    time.sleep(20)
    products_card = driver.find_elements(By.CLASS_NAME,'card-item')
    for product in range(len(products_card)) :
        product_info = products_card[product].text.split('\n')
        if product_info != [''] :
            list_products.append(product_info)
    driver.close()
    return list_products

def generate_data_information(list_product) :
    data = pd.DataFrame()
    for product in list_product :
        temp_dict = {}
        temp_dict['Product Name'] = [product[0]]
        temp_dict['Price'] = [product[-1]]
        if len(product) % 2 == 0 :
            product.pop(1)
        temp_dict['Validity'] = [product[1]]
        for benfefit_name, benefit in zip(product[2:-3:2], product[3:-2:2]):
            temp_dict[benfefit_name] = [benefit]
        temp_data = pd.DataFrame(temp_dict)
        data = pd.concat([data, temp_data])
    return data

list_products = scrape_data(url)
