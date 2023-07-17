import re
import time
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("start-maximized")
webdriver_path = './chromedriver'

def scrape_data(url, iter):
    current_iter = 0
    store_scraped_data = np.array([])
    while current_iter < iter:
        driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        driver.get(url)
        width = 3000
        height = 1000
        driver.set_window_size(width, height)
        if current_iter == 1:
            while True:
                try:
                    driver.find_element(By.XPATH, "//div[@class='listmenu listmenulink false']").click() 
                    time.sleep(3)
                    break
                except:
                    time.sleep(3)
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'slick-track')))
        scraped_data = np.array(driver.find_element(By.CLASS_NAME, 'slick-track').text.split('\n'))
        store_scraped_data = np.concatenate((store_scraped_data, scraped_data))
        current_iter += 1
        driver.close()

    return store_scraped_data

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

def convert_processed_data_to_csv(processed_data):
    data = pd.DataFrame()
    for product in processed_data:
        temp_dict = {}
        temp_dict['Product Name'] = [product[0]]
        temp_dict['Price'] = [product[-2]]
        for benefit_name, benefit in zip(product[1:-2:2], product[2:-2:2]):
            temp_dict[benefit_name] = [benefit]
        temp_data = pd.DataFrame(temp_dict)
        data = pd.concat([data, temp_data])

    return data

def process_product_data(data):
    data.fillna('0', inplace=True)
    data['Price'] = data['Price'].apply(lambda val: val[2:].replace('.', '')).astype('int')

    # Combine columns with similar names
    col_to_drop = [] 
    for index, col1 in enumerate(data.columns):
        for col2 in data.columns[index+1:]:
            if fuzz.ratio(col1, col2) > 90:
                data[col1] = data.apply(lambda row: row[col1] if row[col2] == '0' else row[col2], axis=1)
                col_to_drop.append(col2)
    data.drop(columns=col_to_drop, inplace=True)

    # Extract the amount of quota given by a product
    columns = [
        'Kuota Utama', 
        'Kuota Area', 
        'YouTube', 
        'Kuota Bersama',
        'Masa Aktif'
    ]
    for column in columns:
        data[column] = data[column].apply(lambda val: re.findall(r'(\d+)', val)[0]).astype('float')
    data['Kuota Pribadi'] = data.apply(lambda row: float(re.findall(r'(\d+)', row['Kuota Pribadi'])[0]) * int(re.findall(r'(\d+)', row['Total Anggota'])[0]), axis=1)

    # Combine columns that contains main quota amount
    main_quota = [
        'Kuota Utama',
        'Kuota Area',
        'Kuota Bersama',
        'Kuota Pribadi',   
    ]
    data['Main Quota'] = data.apply(lambda row: row[main_quota].sum(), axis=1) 
    data.drop(columns=main_quota, inplace=True)

    # Process columns that contains application quota
    data['Unlimited Kuota Aplikasi'] = data['Kuota Aplikasi'].apply(lambda val: 1 if val == 'Unlimited' else 0).astype('float')
    data['Kuota Aplikasi'] = data['Kuota Aplikasi'].apply(lambda val: re.findall(r'(\d+)', val)[0] if val != 'Unlimited' else 0).astype('float')
    data['Unlimited Productivity'] = data['Unlimited Productivity'].apply(lambda val: 1 if val == 'Bonus' else val).astype('float')
    data['Unlimited'] = data['Unlimited'].apply(lambda val: 1 if val == 'Whatsapp' else val).astype('float')
    data['Turbo Chat'] = data['Unlimited'].apply(lambda val: 1 if val == 'WhatsApp,Line' else val).astype('float')
    data['YouTube'] = data['YouTube'].astype('float')

    # Combine columns that contains limited application quota
    limited_app_quota = [
        'Kuota Aplikasi',
        'YouTube'
    ]
    data['Limited Application Quota'] = data.apply(lambda row: row[limited_app_quota].sum(), axis=1) 
    data.drop(columns=limited_app_quota, inplace=True)

    # Combine columns that contains unlimited application quota
    unlimited_app_quota = [
        'Unlimited Kuota Aplikasi',
        'Unlimited Productivity',
        'Unlimited',
        'Turbo Chat'
    ]
    data['Unlimited Application Quota'] = data.apply(lambda row: row[unlimited_app_quota].sum(), axis=1) 
    data.drop(columns=unlimited_app_quota, inplace=True)

    # Drop columns that contains information on free calls
    calls = [
        'Telepon Semua Operator',
        'Telepon & SMS ke XL/AXIS',
    ]
    data.drop(columns=calls, inplace=True)

    # Combine columns that contain durations information
    data['Masa Berlaku'] = data['Masa Berlaku'].apply(lambda val: float(re.findall(r'(\d+)', val)[0]) / 24 if val != '0' else 0).astype('float')
    data['Masa Aktif'] = data['Masa Aktif'].astype('float')
    data['Product Duration'] = data.apply(lambda row: row[['Masa Berlaku', 'Masa Aktif']].sum(), axis=1).astype('float')
    data['Product Duration'] = data['Product Duration'].apply(lambda val: 30 if val == 0 else val).astype('float')
    data.drop(columns=['Masa Berlaku', 'Masa Aktif'], inplace=True)

    return data

urls = [
    ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-flex-mc', 1],
    ['https://www.xl.co.id/id/produk/paket-dan-addon/paket-akrab', 1],
    ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-plus', 2],
    ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-mini', 1],
    ['https://www.xl.co.id/id/produk/paket-dan-addon/pilihan-xtra-kuota', 1]
]

xl_products_data_raw = pd.DataFrame()

# for url, iter in urls:
#     scraped_data = scrape_data(url, iter)
#     final_scraped_data = process_scraped_data(scraped_data)
#     product_data = convert_processed_data_to_csv(final_scraped_data)
#     xl_products_data_raw = pd.concat([xl_products_data_raw, product_data])

# xl_products_data_raw.to_csv('XL_Products_Raw.csv', index=False)
xl_products_data_raw = pd.read_csv('XL_Products_Raw.csv')
xl_products_data = process_product_data(xl_products_data_raw)
xl_products_data.to_csv('XL_Products.csv', index=False)