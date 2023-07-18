import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

url = 'https://www.smartfren.com/shop/paket-data-smartfren/'

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


products = scrape_data(url)
data_fix = generate_data_information(products)
print(data_fix)
data_fix.to_csv('data_smartfren.csv',index=False)


def clean_data(data):
    data = data.drop(['Setelah Batas Harian',
                      'Setelah Kuota Utama Habis',
                      'Ke Semua smartfren',
                      'Walau Kuota Habis',
                      'Semua Aplikasi',
                      'Ke Semua Smartfren',
                      'ke Sesama Smartfren'],
                     axis=1)

    column = ['Hingga 4 GB',
              '6 GB']

    for col in column:
        temp_row = data[data[col].isna() == False][col]
        data = data.rename(columns={col: temp_row.values[0]})
        data.at[temp_row.index[0], temp_row.values[0]] = col

    return data


def get_numeric_column(data):
    data = data.fillna(0)
    for i in range(data.shape[0]):

        data['Price'].values[i] = re.findall(r'(\d+\.\d+)', data['Price'].astype(str).values[i])[0]
        data['Validity'].values[i] = re.findall(r'(\d+)', data['Validity'].astype(str).values[i])[0]
        data['Kuota 24 Jam'].values[i] = re.findall(r'(\d+)', data['Kuota 24 Jam'].astype(str).values[i])[0]
        data['Kuota Utama'].values[i] = re.findall(r'(\d+)', data['Kuota Utama'].astype(str).values[i])[0]
        data['Bonus Kuota Lokal'].values[i] = re.findall(r'(\d+)', data['Bonus Kuota Lokal'].astype(str).values[i])[0]
        data['Bonus Kuota'].values[i] = re.findall(r'(\d+)', data['Bonus Kuota'].astype(str).values[i])[0]
        data['Kuota Lokal'].values[i] = re.findall(r'(\d+)', data['Kuota Lokal'].astype(str).values[i])[0]
        data['Kuota Aplikasi'].values[i] = re.findall(r'(\d+)', data['Kuota Aplikasi'].astype(str).values[i])[0]
        if re.findall(r'(\d+) (GB|MB)', data['Setiap Hari'].astype(str).values[i]) != []:
            temp = re.findall(r'(\d+) (GB|MB)', data['Setiap Hari'].astype(str).values[i])[0]
            if 'MB' in temp:
                data['Setiap Hari'].values[i] = int(
                    re.findall(r'(\d+)', data['Setiap Hari'].astype(str).values[i])[0]) / 1000
            else:
                data['Setiap Hari'].values[i] = re.findall(r'(\d+)', data['Setiap Hari'].astype(str).values[i])[0]

    return data

def fixing_column(data) :
    data['Unlimited Main (GB)'] = ['']*data.shape[0]
    for i in range(data.shape[0]) :
        if 'Unlimited' in re.findall(r'Unlimited',data['Product Name'].values[i])  :
            data['Unlimited Main (GB)'].values[i] = float(data['Kuota Utama'].values[i]) + float(data['Setiap Hari'].values[i]) + float(data['Kuota 24 Jam'].values[i]) + float(data['Bonus Kuota Lokal'].values[i]) + float(data['Bonus Kuota'].values[i])
            data['Kuota Utama'].values[i] = 0
        else :
            data['Unlimited Main (GB)'].values[i] = 0
            data['Kuota Utama'].values[i] = float(data['Kuota Utama'].values[i]) + float(data['Kuota 24 Jam'].values[i]) + float(data['Kuota Lokal'].values[i])
    data['Price'] = data['Price'].astype(float)
    data = data[['Product Name','Price','Validity','Kuota Utama','Unlimited Main (GB)','Kuota Aplikasi']]
    data = data.rename(columns={'Kuota Utama':'Limited Main (GB)',
                               'Kuota Aplikasi' : 'Limited Apps (GB)'})
    return data

data_smartfren = data_fix.copy()

data_smartfren = clean_data(data_smartfren)
data_smartfren = get_numeric_column(data_smartfren)
data_smartfren = fixing_column(data_smartfren)
print(data_smartfren)