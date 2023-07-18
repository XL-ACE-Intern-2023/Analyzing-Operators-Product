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


class scrape_xl_functions():
    def __init__(self):
        return

    def scrape_data(self, url, iter):
        current_iter = 0
        store_scraped_data = np.array([])
        while current_iter < iter:
            options = Options()
            options.add_argument("start-maximized")
            webdriver_path = './chromedriver'
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

    def process_scraped_data(self, scraped_data):
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

    def convert_processed_data_to_csv(self, processed_data):
        data = pd.DataFrame()
        for product in processed_data:
            temp_dict = {}
            temp_dict['Product Name'] = [product[0]]
            temp_dict['Price (Rp)'] = [product[-2]]
            for benefit_name, benefit in zip(product[1:-2:2], product[2:-2:2]):
                temp_dict[benefit_name] = [benefit]
            temp_data = pd.DataFrame(temp_dict)
            data = pd.concat([data, temp_data])

        return data

    def _combine_similar_columns(self, dataset):
        col_to_drop = [] 
        for index, col1 in enumerate(dataset.columns):
            for col2 in dataset.columns[index+1:]:
                if fuzz.ratio(col1, col2) > 90:
                    dataset[col1] = dataset.apply(lambda row: row[col1] if row[col2] == '0' else row[col2], axis=1)
                    col_to_drop.append(col2)
        dataset.drop(columns=col_to_drop, inplace=True)

        return dataset
    
    def _process_limited_main_quota_amount(self, dataset):
        columns = [
            'Kuota Utama', 
            'Kuota Area', 
            'Kuota Bersama',
            'Masa Aktif'
        ]
        for column in columns:
            dataset[column] = dataset[column].apply(lambda val: re.findall(r'([0-9.]+)', val)[0]).astype('float')

        dataset['Kuota Pribadi'] = dataset.apply(lambda row: float(re.findall(r'([0-9.]+)', row['Kuota Pribadi'])[0]) * int(re.findall(r'(\d+)', row['Total Anggota'])[0]), axis=1)

        return dataset

    def _process_limited_unlimited_app_quota_amount(self, dataset):
        dataset['Unlimited Kuota Aplikasi'] = dataset['Kuota Aplikasi'].apply(lambda val: 1 if val == 'Unlimited' else 0).astype('float')
        dataset['Kuota Aplikasi'] = dataset['Kuota Aplikasi'].apply(lambda val: re.findall(r'([0-9.]+)', val)[0] if val != 'Unlimited' else 0).astype('float')
        dataset['Unlimited Productivity'] = dataset['Unlimited Productivity'].apply(lambda val: 1 if val == 'Bonus' else val).astype('float')
        dataset['Unlimited'] = dataset['Unlimited'].apply(lambda val: 1 if val == 'Whatsapp' else val).astype('float')
        dataset['Turbo Chat'] = dataset['Unlimited'].apply(lambda val: 1 if val == 'WhatsApp,Line' else val).astype('float')
        dataset['YouTube'] = dataset['YouTube'].apply(lambda val: re.findall(r'([0-9.]+)', val)[0] if len(re.findall(r'([0-9.]+)', val)[0]) > 0 else 0).astype('float')

        return dataset

    def _combine_columns(self, dataset, columns, column_name):
        dataset[column_name] = dataset.apply(lambda row: row[columns].sum(), axis=1) 
        dataset.drop(columns=columns, inplace=True)

        return dataset

    def _process_and_combine_duration_columns(self, dataset):
        dataset['Masa Berlaku'] = dataset['Masa Berlaku'].apply(lambda val: float(re.findall(r'(\d+)', val)[0]) / 24 if val != '0' else 0).astype('float')
        dataset['Masa Aktif'] = dataset['Masa Aktif'].astype('float')
        dataset['Validity Duration (Day)'] = dataset.apply(lambda row: row[['Masa Berlaku', 'Masa Aktif']].sum(), axis=1).astype('float')
        dataset['Validity Duration (Day)'] = dataset['Validity Duration (Day)'].apply(lambda val: 30 if val == 0 else val).astype('float')
        dataset.drop(columns=['Masa Berlaku', 'Masa Aktif'], inplace=True)

        return dataset

    def process_product_data(self, data):
        data.fillna('0', inplace=True)
        data['Price (Rp)'] = data['Price (Rp)'].apply(lambda val: val[2:]).astype('float')
        # Combine columns with similar names
        data = self._combine_similar_columns(data)
        # Extract the amount of quota given by a product
        data = self._process_limited_main_quota_amount(data)
        # Combine columns that contains main quota amount
        limited_main_quota = [
            'Kuota Utama',
            'Kuota Area',
            'Kuota Bersama',
            'Kuota Pribadi',   
        ]
        data = self._combine_columns(data, limited_main_quota, 'Limited Main Quota (GB)')

        # Process columns that contains application quota
        data = self._process_limited_unlimited_app_quota_amount(data)
        
        # Combine columns that contains limited application quota
        limited_app_quota = [
            'Kuota Aplikasi',
            'YouTube'
        ]
        data = self._combine_columns(data, limited_app_quota, 'Limited Application Quota (GB)')

        # Combine columns that contains unlimited application quota
        unlimited_app_quota = [
            'Unlimited Kuota Aplikasi',
            'Unlimited Productivity',
            'Unlimited',
            'Turbo Chat'
        ]
        data = self._combine_columns(data, unlimited_app_quota, 'Unlimited Application Quota (GB)')

        # Drop columns that contains information on free calls
        calls = [
            'Telepon Semua Operator',
            'Telepon & SMS ke XL/AXIS',
        ]
        data.drop(columns=calls, inplace=True)

        # Combine columns that contain durations information
        data = self._process_and_combine_duration_columns(data)

        return data

    def execute(self):
        urls = [
            ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-flex-mc', 1],
            ['https://www.xl.co.id/id/produk/paket-dan-addon/paket-akrab', 1],
            ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-plus', 2],
            ['https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-mini', 1],
            ['https://www.xl.co.id/id/produk/paket-dan-addon/pilihan-xtra-kuota', 1]
        ]

        xl_products_data_raw = pd.DataFrame()

        for url, iter in urls:
            scraped_data = self.scrape_data(url, iter)
            final_scraped_data = self.process_scraped_data(scraped_data)
            product_data = self.convert_processed_data_to_csv(final_scraped_data)
            xl_products_data_raw = pd.concat([xl_products_data_raw, product_data])

        xl_products_data_raw.to_csv('XL_Products_Raw.csv', index=False)
        xl_products_data = self.process_product_data(xl_products_data_raw)
        xl_products_data.to_csv('XL_Products.csv', index=False)

        return xl_products_data_raw
    
xl = scrape_xl_functions()
xl.execute()