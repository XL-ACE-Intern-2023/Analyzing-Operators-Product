import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class scrape_tri_functions():
    def __init__(self):
        return
    
    def scrape_data(self, button_index):
        options = Options()
        options.add_argument("start-maximized")
        webdriver_path = './chromedriver'
        driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        main_url = 'https://my.tri.co.id/data'
        driver.get(main_url)
        scraped_data = []
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='btn action-btn cancel']")))
        driver.find_element(By.XPATH, "//a[@class='btn action-btn cancel']").click()
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, f"//div[@aria-label='{button_index} / 8']")))
        product = driver.find_element(By.XPATH, f"//div[@aria-label='{button_index} / 8']")
        product.click()
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'card-more-btn')))

        for i in range(0, len(driver.find_elements(By.CLASS_NAME, 'card-more-btn'))):
            while True:
                try:
                    product = driver.find_element(By.XPATH, f"//div[@aria-label='{button_index} / 8']")
                    product.click()
                    break
                except:
                    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, f"//div[@aria-label='{button_index} / 8']")))
            while True:
                try:
                    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='card-more-btn']")))
                    buttons = driver.find_elements(By.XPATH, "//div[@class='card-more-btn']")
                    buttons[i].click()
                    time.sleep(3)
                    infos = driver.find_elements(By.XPATH, "//div[@class='card-body']")
                    try:
                        for info in infos:
                            if info.text != '':
                                scraped_data.append(info.text.split('\n'))
                    except:
                        scraped_data.append(infos.text.split('\n'))
                    break
                except:
                    pass

            driver.back()

        return scraped_data

    def process_scraped_data(self, scraped_data):
        processed_data = []
        for row in scraped_data:
            row.remove('Rincian Paket')
            row.remove('Perpanjang otomatis')
            try:
                row.remove('Ya')
            except:
                row.remove('Tidak')
            row.remove('Beli')
            processed_data.append(row)

        return processed_data
        
    def convert_processed_data_to_csv(self, processed_data):
        processed_data_df = pd.DataFrame()
        
        for row in processed_data:
            temp_dict = {}
            temp_dict['Product Name'] = [row[-1]]
            temp_dict['Price'] = [row[-2]]

            kuota_index = []
            for index, val in enumerate(row[:-2]):
                if val.split()[0] == 'Kuota':
                    kuota_index.append(index)
            kuota_index.append(len(row[:-2]))
            
            for i in range(len(kuota_index)-1):
                start_index = kuota_index[i]
                end_index = kuota_index[i+1]
                benefit_name = row[start_index]
                temp_row = row[start_index:end_index]

                if benefit_name == 'Kuota Weekend':
                    benefit_active = 'Weekend'
                    benefit_amount = temp_row[1]
                    benefit_duration = temp_row[2]
                    
                elif benefit_name == 'Kuota Tiktok' or benefit_name == 'Kuota Streaming':
                    benefit_active = temp_row[1]
                    benefit_amount = temp_row[2]
                    benefit_duration = temp_row[3]
                    
                elif benefit_name == 'Kuota Reguler' and len(temp_row) == 4:
                    benefit_active = temp_row[1]
                    benefit_amount = temp_row[2]
                    benefit_duration = temp_row[3]

                elif benefit_name == 'Kuota Reguler' and len(temp_row) == 3:
                    benefit_active = '24 Jam'
                    benefit_amount = temp_row[1]
                    benefit_duration = 'Berlaku 30 Hari'
                    
                elif benefit_name == 'Kuota 01.00-17.00':
                    benefit_active = '01.00-17.00'
                    benefit_amount = temp_row[1]
                    benefit_duration = 'Berlaku 30 Hari'
                    
                elif benefit_name == 'Kuota 01.00-06.00 dan 15.00-18.00':
                    benefit_active = '01.00-06.00 and 15.00-18.00'
                    benefit_amount = temp_row[1]
                    benefit_duration = temp_row[2]
                    
                elif benefit_name == 'Kuota AON':
                    benefit_active = temp_row[2]
                    benefit_amount = temp_row[1]
                    benefit_duration = 'Berlaku 365 Hari'

                elif benefit_name == 'Kuota Nasional':
                    benefit_active = temp_row[1]
                    benefit_amount = temp_row[2]
                    benefit_duration = temp_row[3]

                elif benefit_name == 'Kuota 01.00 - 05.59':
                    benefit_active = '01.00-05.59'
                    benefit_amount = temp_row[1]
                    benefit_duration = temp_row[2]

                elif benefit_name == 'Kuota 01.00 - 09.00':
                    benefit_active = '01.00-09.00'
                    benefit_amount = temp_row[1]
                    benefit_duration = temp_row[2] 
                    
                elif benefit_name == 'Kuota 4G':
                    benefit_active = '24 Jam'
                    benefit_amount = temp_row[1]
                    benefit_duration = temp_row[2] 

                temp_dict[f'{benefit_name} Active'] =  [benefit_active]
                temp_dict[f'{benefit_name} Amount'] =  [benefit_amount]
                temp_dict[f'{benefit_name} Duration'] =  [benefit_duration]
                
            temp_processed_data_df = pd.DataFrame(temp_dict)
            processed_data_df = pd.concat([processed_data_df, temp_processed_data_df])

        return processed_data_df

    def _create_column(self, dataset, columns, column_name):
        columns_amount = [f'{val} Amount' for val in columns]
        columns_duration = [f'{val} Duration' for val in columns]
        dataset[f'{column_name} (GB)'] = dataset.apply(lambda row: row[columns_amount].sum(), axis=1)
        dataset.drop(columns=columns_amount, inplace=True)
        dataset[f'{column_name} Duration (Hari)'] = dataset.apply(lambda row: row[columns_duration].max(), axis=1)
        dataset.drop(columns=columns_duration, inplace=True)    

        return dataset

    def _process_columns(self, dataset):
        for column in dataset.columns:
            if column.split()[-1] == 'Amount':
                dataset = dataset.loc[dataset[column] != 'Unlimited', :] 
                dataset[column] = dataset[column].apply(lambda val: val[:-2] if val[-2:] == 'GB' else val).astype('float')
            elif column.split()[-1] == 'Duration':
                dataset[column] = dataset[column].apply(lambda val: re.findall(r'(\d+) hari', val.lower())[0] if len(re.findall(r'(\d+) hari', val.lower())) > 0 else 0).astype('float')
            elif column.split()[-1] == 'Active':
                dataset.drop(columns=[column], inplace=True)
        
        return dataset

    def process_product_data(self, processed_data_df):
        processed_data_df['Price'] = processed_data_df['Price'].apply(lambda val: val[2:]).astype('float')
        processed_data_df.fillna('0', inplace=True)

        processed_data_df = self._process_columns(processed_data_df)

        limited_main_quota = [
            'Kuota Nasional', 
            'Kuota Reguler',
            'Kuota Weekend', 
            'Kuota 01.00-17.00', 
            'Kuota 01.00-06.00 dan 15.00-18.00',
            'Kuota AON',
            'Kuota Harian',
            'Kuota 01.00 - 05.59',
            'Kuota 01.00 - 09.00',
            'Kuota 4G'
        ]

        processed_data_df = self._create_column(processed_data_df, limited_main_quota, 'Limited Main Quota')

        limited_app_quota = [
            'Kuota Streaming'
        ]

        processed_data_df = self._create_column(processed_data_df, limited_app_quota, 'Limited App Quota')

        unlimited_app_quota = [
            'Kuota Tiktok'
        ]

        processed_data_df = self._create_column(processed_data_df, unlimited_app_quota, 'Unlimited App Quota')

        processed_data_df['Product Duration (Hari)'] = processed_data_df.apply(lambda row: row[['Limited Main Quota Duration (Hari)', 'Limited App Quota Duration (Hari)', 'Unlimited App Quota Duration (Hari)']].max() , axis=1)  

        return processed_data_df
    
    def execute(self):
        tri_products_data_raw = pd.DataFrame()
        for i in range(1, 9):
            if i == 7:
                pass
            else:
                scraped_data = self.scrape_data(i)
                processed_data = self.process_scraped_data(scraped_data)
                temp_raw = self.convert_processed_data_to_csv(processed_data)
                tri_products_data_raw = pd.concat([tri_products_data_raw, temp_raw])
            
        tri_products_data_raw.to_csv('Tri_Products_Raw.csv', index=False)
        tri_products_data = self.process_product_data(tri_products_data_raw)
        tri_products_data.to_csv('Tri_Products.csv', index=False)

        return tri_products_data