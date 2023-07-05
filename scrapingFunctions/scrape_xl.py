import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("start-maximized")
webdriver_path = './chromedriver'

def scrape_data(url):
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
    driver.get(url)
    width = 3000
    height = 1000
    driver.set_window_size(width, height)
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'slick-track')))
    product_info = np.array(driver.find_element(By.CLASS_NAME, 'slick-track').text.split('\n'))
    driver.close()

    return product_info

def process_scraped_data(scraped_data):
    n_reshape = np.where(scraped_data == 'Beli Paket')[0][0] + 1
    reshaped = scraped_data.reshape(-1, n_reshape)
    final_scraped_data = []
    for product in reshaped:
        length = len(product)
        if product[length-3][:2] == 'Rp':
            cleaned =  np.delete(product, length-3)
            final_scraped_data.append(cleaned)
        else:
            final_scraped_data.append(product)
    
    return np.array(final_scraped_data)

def convert_scraped_data_to_csv(scraped_data):
    data = pd.DataFrame()
    for product in scraped_data:
        temp_dict = {}
        temp_dict['Product Name'] = [product[0]]
        for benfefit_name, benefit in zip(product[1:-1:2], product[2:-1:2]):
            temp_dict[benfefit_name] = [benefit]
        temp_data = pd.DataFrame(temp_dict)
        data = pd.concat([data, temp_data])

    return data


urls = [
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-flex-mc',
    'https://www.xl.co.id/id/produk/paket-dan-addon/paket-akrab',
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-plus',
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-mini',
    'https://www.xl.co.id/id/produk/paket-dan-addon/pilihan-xtra-kuota'
]

xl_products_data = pd.DataFrame()
for url in urls:
    scraped_data = scrape_data(url)
    final_scraped_data = process_scraped_data(scraped_data)
    product_data = convert_scraped_data_to_csv(final_scraped_data)
    xl_products_data = pd.concat([xl_products_data, product_data])

xl_products_data.to_csv('XL_Products.csv', index=False)