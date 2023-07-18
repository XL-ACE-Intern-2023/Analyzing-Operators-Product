import re
import time
import selenium
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

class scrape_indosat_function:
    def __init__(self):
        return

    # FREEDOM INTERNET

    def paket_freedom_internet (self) :
        driver.get("https://indosatooredoo.com/portal/id/psfreedominternet")
        width = 2800
        height = 1200
        driver.set_window_size(width, height)
        list_href = ['tabid_10021','tabid_10032','tabid_10043']

        dframe = pd.DataFrame()

        for href in list_href :
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,"//a[@href= '{}']".format(str(href)))))
            produkdata = driver.find_element(By.XPATH,"//a[@href= '{}']".format(str(href)))
            produkdata.click()

            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID,"tabelements_packs")))
            list_products = driver.find_element(By.ID,"tabelements_packs").text.split("\n")

            list_product = []
            for info in list_products :
                row = {}

                if info != 'Lihat detail' :
                    list_product.append(info)
                    # print(info)
                    continue
                else :
                    row['Operator'] = 'Indosat'
                    row['Produk'] = list_product[0]

                    index_harga_and_valid = list_product.index("HARGA")+1
                    row['Harga'] = re.findall(r"Rp (\d+(?:\.\d+)?)",list_product[int(index_harga_and_valid)])[0]
                    row['Masa Berlaku (Hari)'] = re.findall(r"(\d+) Hari",list_product[int(index_harga_and_valid)])[0]

                    row['Kuota Utama Terbatas (GB)'] = re.findall(r"Freedom Internet (\d+(?:\.\d+)?)GB",list_product[0])[0]
                    row['Kuota Aplikasi Terbatas (GB)'] = 0
                    row['Kuota Utama Tidak Terbatas (GB)'] = 0
                    row['Kuota Aplikasi Tidak Terbatas (GB)'] = 0


                    row['Lainnya'] = np.nan

                    # print(row)
                    row_df = pd.DataFrame(row, index = [0])
                    dframe = pd.concat([dframe,row_df])

                    list_product = []

        return dframe

    # FREEDOM U

    def paket_freedom_u (self) :
        driver.get("https://indosatooredoo.com/portal/id/psfreedomu")
        time.sleep(2)
        lihat_detail_elements = driver.find_elements(By.XPATH,"//a[@ng-click='detailedpage(pack)']")
        list_products = []

        for i in range(len(lihat_detail_elements)) :
            lihat_detail_elements[i].click()
            time.sleep(3)
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
                # print(list_product)
                row['Operator'] = 'Indosat'
                row['Produk'] = list_product[0]
                row['Harga'] = re.findall(r"Rp (\d+(?:\.\d+)?)",list_product[1])[0]
                row['Masa Berlaku (Hari)'] = re.findall(r"(\d+) Hari",list_product[1])[0]

                index_main_quota = list_product.index('Kuota utama') + 1
                try :
                    index_apps_quota = list_product.index('Kuota aplikasi') + 1
                    row['Kuota Aplikasi Terbatas (GB)'] = re.findall(r"(\d+) GB", list_product[index_apps_quota])[0]
                except :
                    row['Kuota Aplikasi Terbatas (GB)'] = 0

                row['Kuota Utama Terbatas (GB)'] = re.findall(r"(\d+) GB", list_product[index_main_quota])[0]
                row['Kuota Utama Tidak Terbatas (GB)'] = 0
                row['Kuota Aplikasi Tidak Terbatas (GB)'] = 0


                row['Lainnya'] = np.nan

                # print(row)

                row_df = pd.DataFrame(row, index = [0])
                dframe = pd.concat([dframe,row_df])

                list_product = []

        return dframe

    def combine_then_rename_columns(self,df1,df2):

        dframe = pd.concat([df1,df2],axis=0).reset_index().drop(['index'],axis=1)

        rename_dict = {

            "Operator" : "Operator",
            "Produk" : "ProductName",
            "Harga" : "Price (Rp)",
            "Masa Berlaku (Hari)" : "Validity Duration (Day)",
            "Kuota Utama Terbatas (GB)" : "Limited Main Quota (GB)",
            "Kuota Utama Tidak Terbatas (GB)" : "Unlimited Main Quota (GB)",
            "Kuota Aplikasi Terbatas (GB)" : "Limited Application Quota (GB)",
            "Kuota Aplikasi Tidak Terbatas (GB)": "Unlimited Application Quota (GB)",
            "Lainnya" : "Others"

        }
        dframe = dframe.rename(columns=rename_dict)

        return dframe

    def execute(self):
        df_freedom_internet = self.paket_freedom_internet()
        df_freedom_u = self.paket_freedom_u()

        df_combined = self.combine_then_rename_columns(df_freedom_internet,df_freedom_u)

        return df_combined

indosat_func = scrape_indosat_function()

indosat_func.execute().to_csv("Indosat_Products.csv")