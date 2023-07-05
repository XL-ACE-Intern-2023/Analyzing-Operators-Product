import time
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

def scrape_data(button_index):
    driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
    main_url = 'https://my.tri.co.id/data'
    driver.get(main_url)

    time.sleep(5)
    _ = driver.find_elements(By.CLASS_NAME, 'card-body')[2::2][button_index].click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'card-more-btn')))
    buttons = driver.find_elements(By.CLASS_NAME, 'card-more-btn')

    products_info = []
    for i in range(4):
        while True:
            try:
                buttons[i].click()
                break
            except:
                buttons = driver.find_elements(By.CLASS_NAME, 'card-more-btn')

        time.sleep(3)
        infos = driver.find_elements(By.CLASS_NAME, 'card-body')
        try:
            for info in infos:
                if info.text != '':
                    products_info.append(info.text.split('\n'))
        except:
            products_info.append(infos.text.split('\n'))
        driver.back()
            
    return products_info

def process_scraped_data(scraped_data):
    for index, product in enumerate(scraped_data):
        product.remove('Rincian Paket')
        product.remove('Perpanjang otomatis')
        product.remove('Ya')
        product.remove('Beli')
        scraped_data[index] = product
 
    return scraped_data


scraped_data = scrape_data(0)
print(process_scraped_data(scraped_data))