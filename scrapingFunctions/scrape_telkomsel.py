import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC

list_url = ['https://www.telkomsel.com/shops/digital-product/package?utm_source=wec&utm_medium=quickbutton&utm_campaign=belipaket&utm_id=wec-isipaket&msisdn=&type=internet&category=Semua%20Paket&roaming=&service=PraBayar&sort=&minPrice=&maxPrice=&quota=',
       'https://www.telkomsel.com/shops/digital-product/package?utm_source=wec&utm_medium=quickbutton&utm_campaign=belipaket&utm_id=wec-isipaket&msisdn=&type=entertainment&category=Semua%20Paket&roaming=&service=PraBayar&sort=&minPrice=&maxPrice=&quota=']

def scrape_data(url) :
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(30)
    list_card = driver.find_elements(By.XPATH, "//div[@class='card-item enabled']")
    list_products = []
    for card in list_card:
        driver.execute_script("arguments[0].click();", card)
        time.sleep(1)
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='cardPackage']")))
        detail_card = driver.find_element(By.XPATH, "//div[@id='cardPackage']")
        list_products.append(detail_card.text.split('\n'))
        time.sleep(1)
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='w-6 inline cursor-pointer bg-close']")))
        driver.find_element(By.XPATH, "//div[@class='w-6 inline cursor-pointer bg-close']").click()
    driver.close()
    return list_products

def generate_data_information(list_product) :
    data = pd.DataFrame()
    for product in list_product :
        temp_dict = {}
        product.remove('Deskripsi')
        product.remove('Syarat dan Ketentuan')
        #product.remove('Harga Total')
        #product.remove('Beli')
        product.pop(-1)
        if product[0] =='PROMO' :
            product.pop(0)
            product.pop(3)
            product.pop(3)
        temp_dict['Product Name'] = [product[0]]
        temp_dict['Price'] = [product[1]]

        if len(product) % 2 == 0 :
            for benfefit_name, benefit in zip(product[2:-2:2], product[3:-1:2]):
                temp_dict[benfefit_name] = [benefit]
            temp_data = pd.DataFrame(temp_dict)
        else :
            temp_dict['Validity'] = [product[2]]
            for benfefit_name, benefit in zip(product[3:-2:2], product[4:-1:2]):
                temp_dict[benfefit_name] = [benefit]
            temp_data = pd.DataFrame(temp_dict)

        data = pd.concat([data, temp_data])

    return data

list_products = []
for url in list_url :
    product = scrape_data(url)
    list_products.extend(product)
data_fix = generate_data_information(list_products)
print(data_fix)
data_fix.to_csv('data_telkomsel_fix3.csv',index=False)

data = data_fix.copy()

list_non_quota = ['Nelpon Tsel',
                 'Operator lain',
                 'Nelpon',
                 'SMS',
                 'Pembelian Obat',
                  'Voucher Tinder Plus',
                  'Prime Video',
                  'Telekonsultasi Halodoc',
                  'Pembelian Obat',
                  'Zoom Pro',
                  'Fita Exercise Plan',
                  'Fita Premium',
                  'Allianz',
                  'Roaming Haji',
                  'Roamax Negara Transit',
                  'Langit Musik',
                  'NSP',
                  'Smule',
                  'Langganan Premium Video',
                  'Movie Lovers Basic',
                  'Lionsgate Play',
                  'Vision+',
                  'Prime Video Mobile',
                  'WeTV',
                  'Viu',
                  'Langganan Video',
                  'Disney+ Hotstar',
                  'Vidio Platinum',
                  'Vidio Platinum Mobile']

list_benefit = ['Pembelian Obat',
                  'Voucher Tinder Plus',
                  'Prime Video',
                  'Telekonsultasi Halodoc',
                  'Pembelian Obat',
                  'Zoom Pro',
                  'Fita Exercise Plan',
                  'Fita Premium',
                  'Allianz',
                  'Roaming Haji',
                  'Roamax Negara Transit',
                  'Langit Musik',
                  'NSP',
                  'Smule',
                  'Langganan Premium Video',
                  'Movie Lovers Basic',
                  'Lionsgate Play',
                  'Vision+',
                  'Prime Video Mobile',
                  'WeTV',
                  'Viu',
                  'Langganan Video',
                  'Disney+ Hotstar',
                  'Vidio Platinum',
                  'Vidio Platinum Mobile']


def fixing_columns(data, list_drop_col, list_benefit_col):
    data['Other Benefit'] = [''] * data.shape[0]
    for col in list_benefit_col:
        indeks = data.loc[data[col].isna() == False].index
        for i in indeks:
            data.at[i, 'Other Benefit'] = col

    data = data.drop(list_drop_col, axis=1)
    data = data.fillna(0)

    return data

def get_values(data) :
    list_regex = [r'(\d+)',r'(\d+\.\d+)',r'(\d+)']
    for col in list(data.columns)[1:-1] :
        for i in range(data.shape[0]) :
            for regex in list_regex :
                temp_val_regex = re.findall(regex, data[col].astype(str).values[i])
                if temp_val_regex != [] :
                    if len(temp_val_regex) == 1 :
                        data[col].values[i] = temp_val_regex[0]
                        break
    return data


def merge_columns_val(data):
    data['Limited Main (GB)'] = [0] * data.shape[0]
    data['Limited Apps (GB)'] = [0] * data.shape[0]
    list_main = ['Internet',
                 'Internet Lokal']

    list_apps = ['DPI Tinder', 'Kuota Apps', 'Ilmupedia',
                 'Ruangguru', 'Belajar', 'Apps', 'Facebook',
                 'Instagram', 'TikTok', 'Twitter', 'YouTube', 'Whatsapp',
                 'Kuota Halodoc', 'Kuota Zoom', 'Youtube',
                 'Kuota Nonton', 'Kuota Chat', 'Kuota Sosmed', 'Kuota Fita', 'Games',
                 'Smule VIP', 'Kuota Youtube', 'Internet Musik', 'JOOX VIP', 'MAXstream']

    for main_col in list_main:
        data['Limited Main (GB)'] += data[main_col].astype(float)

    for apps_col in list_apps:
        data['Limited Apps (GB)'] += data[apps_col].astype(float)

    list_index = []
    for i in range(data.shape[0]):
        if data['Limited Main (GB)'].values[i] == 0 and data['Limited Apps (GB)'].values[i] == 0:
            list_index.append(i)
    data = data.drop(list_index).reset_index(drop=True)
    data['Price'] = data['Price'].astype(float)
    data = data[['Product Name', 'Price', 'Validity', 'Limited Main (GB)', 'Limited Apps (GB)', 'Other Benefit']]

    return data

data = fixing_columns(data, list_non_quota, list_benefit)
data = get_values(data)
data = merge_columns_val(data)
print(data)