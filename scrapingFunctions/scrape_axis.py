import selenium
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


driver = webdriver.Chrome()


list_url = ['https://www.axis.co.id/produk/paket-internet/axis-owsem',
            'https://www.axis.co.id/produk/paket-internet/paket-bronet-axis-kuota-24-jam/harian',
            'https://www.axis.co.id/produk/paket-internet/paket-kuota-aplikasi-boostr-axis/',
            'https://www.axis.co.id/produk/paket-internet/paket-warnet']





# Paket Owsem

def axis_owsem(url) :
    driver.get(str(url))
    time.sleep(2)
    list_owsem = driver.find_element(By.CLASS_NAME, 'internet-package-wrapper').text.split("\n")

    driver.close()

    dframe = pd.DataFrame()

    list_product = []
    for info in list_owsem:
        row = {}

        if info != 'Unlimited' :
            list_product.append(info)
            continue

        else:
            if list_product[0] == 'GB' :
                list_product.pop(0)

            row['Operator'] = 'AXIS'
            row['Produk'] = "AXIS Owsem" + " " + (" ".join(list_product[:4]))
            row['Harga'] = float(list_product[3])
            row['Masa Berlaku (Hari)'] = int(re.findall(r"Masa aktif (\d+) hari", list_product[4])[0])

            index_main_quota = list_product.index('Kuota Utama') + 1
            index_night_quota = list_product.index('Kuota Malam 00.00 - 06.00') + 1

            row['Kuota Utama (GB)'] = float(list_product[index_main_quota]) + float(list_product[index_night_quota])

            index_vid_quota = list_product.index('Kuota Video') + 1
            index_soc_quota = list_product.index('Kuota Sosmed') + 1
            index_mus_quota = list_product.index('Kuota Musik') + 1

            row['Kuota Aplikasi (GB)'] = float(list_product[index_vid_quota]) + float(
                list_product[index_soc_quota]) + float(list_product[index_mus_quota])
            row['Fair Usage Policy (GB)'] = 0
            # print(row)

            row_df = pd.DataFrame(row, index=[0])
            dframe = pd.concat([dframe, row_df])

            list_product = []

    return dframe



# dframe1 = axis_owsem(list_url[0])


# Paket Kuota Aplikasi BOOSTR

def axis_boostr (origin_url) :
    driver.get(origin_url)

    sections = ['video','musik','sosmed','edukasi','games','konferensi','sunset','komik']

    dframe = pd.DataFrame()

    for section in sections :
        url = origin_url + str(section)
        driver.get(str(url))

        if section == 'sunset' : # Kuota Utama
            list_boostr_main = driver.find_element(By.CLASS_NAME, 'internet-package-wrapper').text.split('\n')

            list_product = []
            for info in list_boostr_main:
                row = {}

                if info != 'Beli' :
                    list_product.append(info)
                    continue

                else:
                    if list_product[0] == 'Kuota 17.00 - 20.00' :
                        del list_product[:3]


                    row['Operator'] = 'AXIS'
                    row['Produk'] = "AXIS BOOSTR " + str(section) + " " + (" ".join(list_product[:4]))
                    row['Harga'] = float(list_product[3])
                    row['Masa Berlaku (Hari)'] = int(re.findall(r"Masa aktif (\d+) hari", list_product[4])[0])

                    row['Kuota Utama (GB)'] = float(list_product[0])

                    row['Kuota Aplikasi (GB)'] = 0
                    row['Fair Usage Policy (GB)'] = 0
                    # print(row)

                    row_df = pd.DataFrame(row, index=[0])
                    dframe = pd.concat([dframe, row_df])

                    list_product = []

            time.sleep(1)

        else : # Kuota Aplikasi
            list_boostr_app = driver.find_element(By.CLASS_NAME, 'internet-package-wrapper').text.split('\n')

            stops = ['Kuota Video', 'Kuota Musik', 'Kuota Sosmed', 'Kuota Edukasi', 'Kuota Game', 'Kuota Komik', 'Kuota Konferensi']

            list_product = []
            for info in list_boostr_app:
                row = {}

                if info != 'Beli' :
                    list_product.append(info)
                    continue

                else:
                    if list_product[0] in stops :
                        del list_product[:3]

                    row['Operator'] = 'AXIS'
                    row['Produk'] = "AXIS BOOSTR " + str(section) + " " + (" ".join(list_product[:4]))
                    row['Harga'] = float(list_product[3])
                    row['Masa Berlaku (Hari)'] = int(re.findall(r"Masa aktif (\d+) hari", list_product[4])[0])

                    row['Kuota Utama (GB)'] = 0

                    row['Kuota Aplikasi (GB)'] = float(list_product[0])
                    row['Fair Usage Policy (GB)'] = 0
                    # print(row)

                    row_df = pd.DataFrame(row, index=[0])
                    dframe = pd.concat([dframe, row_df])

                    list_product = []

    driver.close()

    return dframe

# dframe2 = axis_boostr(list_url[2])


# Paket Kuota Warnet


def axis_warnet(url) :

    driver.get(url)

    # Section 1 : Paket Internet Warnet

    paketwarnet1 = driver.find_element(By.XPATH,"//div[@class = 'container py-main pb-0 pt-0']").text.split("\n")
    paketwarnet1.pop(0)
    print(paketwarnet1)

    dframe = pd.DataFrame()
    list_product = []
    for info in paketwarnet1 :
        row = {}

        if info != 'Beli' :
            list_product.append(info)
            continue

        else:

            row['Operator'] = 'AXIS'
            row['Produk'] = "AXIS " + "Warnet" + " " + (" ".join(list_product[:4]))
            row['Harga'] = float(list_product[3])
            row['Masa Berlaku (Hari)'] = int(re.findall(r"Masa aktif (\d+) jam", list_product[4])[0])

            row['Kuota Utama (GB)'] = float(list_product[0].replace(",","."))

            row['Kuota Aplikasi (GB)'] = 0
            row['Fair Usage Policy (GB)'] = 0
            # print(row)

            row_df = pd.DataFrame(row, index=[0])
            dframe = pd.concat([dframe, row_df])

            list_product = []

    # Section 2 : Paket Internet Warnet + Game Token

    games = ["mobile-legend", "free-fire", "arena-of-valor", "call-of-duty-mobile"]
    games_item = {"mobile-legend" : "DIAMOND",
                       "free-fire" : "DIAMOND",
                       "arena-of-valor" : "VOUCHERS",
                       "call-of-duty-mobile" : "CP"
    }

    for game in games :
        time.sleep(2)
        driver.get("https://www.axis.co.id/produk/paket-internet/paket-warnet?token={}".format(game))
        paketwarnet2_pergame = driver.find_element(By.XPATH, "//section[@class = 'py-main pt-0 sc-pilih-paket-token']").text.split("\n")
        for i in range (0,5) :
            paketwarnet2_pergame.pop(0)

        dframe = pd.DataFrame()
        list_product = []
        for info in paketwarnet2_pergame :
            row = {}

            if info != str(games_item[game]) :
                list_product.append(info)
                continue

            else:

                row['Operator'] = 'AXIS'
                row['Produk'] = "AXIS " + "Warnet " + ("{} ".format(str(game))) + (" ".join(list_product[:4]))
                row['Harga'] = float(list_product[3])
                row['Masa Berlaku (Hari)'] = int(re.findall(r"Masa aktif (\d+) jam", list_product[4])[0])

                row['Kuota Utama (GB)'] = float(list_product[0].replace(",","."))

                row['Kuota Aplikasi (GB)'] = 0
                row['Fair Usage Policy (GB)'] = 0
                row[str(games_item[game])] = list_product[-1]
                # print(row)

                row_df = pd.DataFrame(row, index=[0])
                dframe = pd.concat([dframe, row_df])

                list_product = []

    driver.close()

    return dframe

# dframe3 = axis_warnet(list_url[3])
