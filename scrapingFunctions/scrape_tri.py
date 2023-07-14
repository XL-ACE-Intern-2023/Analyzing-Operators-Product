import time
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
    width = 1000
    height = 3000
    driver.set_window_size(width, height)
    scraped_data = []
    time.sleep(3)
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
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'card-more-btn')))
                buttons = driver.find_elements(By.CLASS_NAME, 'card-more-btn')
                buttons[i].click()
                time.sleep(1)
                infos = driver.find_elements(By.CLASS_NAME, 'card-body')
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
        driver.refresh()

    return scraped_data

def process_scraped_data(scraped_data):
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
    
def convert_processed_data_to_csv(processed_data):
    df = pd.DataFrame()
    
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

            temp_dict[f'{benefit_name} Active'] =  [benefit_active]
            temp_dict[f'{benefit_name} Amount'] =  [benefit_amount]
            temp_dict[f'{benefit_name} Duration'] =  [benefit_duration]
               
        temp_df = pd.DataFrame(temp_dict)
        df = pd.concat([df, temp_df])

    return df

df_combined = pd.DataFrame()
for i in range(1, 9):
    if i == 7:
        pass
    else:
        scraped_data = scrape_data(i)
        processed_data = process_scraped_data(scraped_data)
        df = convert_processed_data_to_csv(processed_data)
        df_combined = pd.concat([df_combined, df])
    
df_combined.to_csv('Tri_Products.csv', index=False)