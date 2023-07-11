import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
driver = webdriver.Chrome()

list_url = ['https://www.smartfren.com/shop/paket-data-smartfren/#tab-prabayar',
       'https://www.smartfren.com/shop/paket-data-smartfren/#tab-elite-paskabayar',
       'https://www.smartfren.com/shop/paket-data-smartfren/#tab-roaming']

def scrape_data(url) :
    driver = webdriver.Chrome()
    driver.get(url)
    list_products = []
    time.sleep(10)
    products_card = driver.find_elements(By.CLASS_NAME,'product-card')
    for product in range(len(products_card)) :
        product_info = products_card[product].text.split('\n')
        if product_info != [''] :
            product_info.remove('BELI')
            list_products.append(product_info)
    driver.close()
    return list_products

def generate_data_information(list_product) :
    data = pd.DataFrame()
    for product in list_product :
        temp_dict = {}
        temp_dict['Product Name'] = [product[0] + ' ' + product[1]]
        temp_dict['Price'] = [product[-1]]
        if len(product) % 2 == 0 :
                temp_dict['Validity'] = [product[-2]]
        for benfefit_name, benefit in zip(product[3:-2:2], product[2:-3:2]):
            temp_dict[benfefit_name] = [benefit]
        temp_data = pd.DataFrame(temp_dict)
        data = pd.concat([data, temp_data])
    return data

def generate_unique_product(list_product):
    unique_list = []
    seen = set()

    for item in list_product :
        item_tuple = tuple(item)
        if item_tuple not in seen:
            unique_list.append(item)
            seen.add(item_tuple)
    return unique_list

list_product = []
print(len(list_product))
for url in list_url :
    products = scrape_data(url)
    list_product.extend(products)
list_product = generate_unique_product(list_product)
print(len(list_product))
print(generate_data_information(list_product))
data_fix = generate_data_information(list_product)
data_fix.to_csv('datot.csv',index=False)