import re
import time
import selenium
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

class indosat:
    def __init__(self):
        return

    # FREEDOM INTERNET

    def paket_freedom_internet (self) :
        driver.get("https://indosatooredoo.com/portal/id/psfreedominternet")
        time.sleep(2) # Waktu buat pencet fullscreen
        list_href = ['tabid_10021','tabid_10032','tabid_10043']

        dframe = pd.DataFrame()

        for href in list_href :

            produkdata = driver.find_element(By.XPATH,"//a[@href= '{}']".format(str(href)))
            produkdata.click()
            time.sleep(3)

            list_products = driver.find_element(By.ID,"tabelements_packs").text.split("\n")
            print(list_products)

            list_product = []
            for info in list_products :
                row = {}

                if info != 'Lihat detail' :
                    list_product.append(info)
                    print(info)
                    continue
                else :
                    row['Operator'] = 'Indosat'
                    row['Produk'] = list_product[0]

                    index_harga_and_valid = list_product.index("HARGA")+1
                    row['Harga'] = re.findall(r"Rp (\d+(?:\.\d+)?)",list_product[int(index_harga_and_valid)])[0]
                    row['Masa Berlaku (Hari)'] = re.findall(r"(\d+) Hari",list_product[int(index_harga_and_valid)])[0]

                    row['Kuota Utama (GB)'] = re.findall(r"Freedom Internet (\d+(?:\.\d+)?)GB",list_product[0])[0]
                    row['Kuota Aplikasi (GB)'] = 0
                    row['Fair Usage Policy (GB)'] = 0

                    row_df = pd.DataFrame(row, index = [0])
                    dframe = pd.concat([dframe,row_df])

                    list_product = []

        driver.close()

        return dframe


    # FREEDOM U

    def paket_freedom_u (self) :

        driver.get("https://indosatooredoo.com/portal/id/psfreedomu")

        lihat_detail_elements = driver.find_elements(By.XPATH,"//a[@ng-click='detailedpage(pack)']")
        list_products = []

        for i in range(len(lihat_detail_elements)) :
            lihat_detail_elements[i].click()
            time.sleep(5)
            list_products = list_products + driver.find_element(By.XPATH, "//div[@class='row ng-scope']").text.split('\n')
            driver.back()
            lihat_detail_elements = driver.find_elements(By.XPATH, "//a[@ng-click='detailedpage(pack)']")
            time.sleep(2)

        driver.close()

        dframe = pd.DataFrame()
        list_product = []
        for info in list_products :
            row = {}

            if info != 'BELI' :
                list_product.append(info)
                continue
            else :
                row['Operator'] = 'Indosat'
                row['Produk'] = list_product[0]
                row['Harga'] = re.findall(r"Rp (\d+(?:\.\d+)?)",list_product[1])[0]
                row['Masa Berlaku (Hari)'] = re.findall(r"(\d+) Hari",list_product[1])[0]

                index_main_quota = list_product.index('Kuota utama') + 1
                try :
                    index_apps_quota = list_product.index('Kuota aplikasi') + 1
                    row['Kuota Aplikasi (GB)'] = re.findall(r"(\d+) GB", list_product[index_apps_quota])[0]
                except :
                    row['Kuota Aplikasi (GB)'] = 0

                row['Kuota Utama (GB)'] = re.findall(r"(\d+) GB", list_product[index_main_quota])[0]
                row['Fair Usage Policy (GB)'] = 0

                row_df = pd.DataFrame(row, index = [0])
                dframe = pd.concat([dframe,row_df])

                list_product = []

        return dframe