import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

urls = [
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-flex-mc',
    'https://www.xl.co.id/id/produk/paket-dan-addon/paket-akrab',
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-plus',
    'https://www.xl.co.id/id/produk/paket-dan-addon/xtra-combo-mini',
    'https://www.xl.co.id/id/produk/paket-dan-addon/pilihan-xtra-kuota'
]

options = Options()
options.add_argument("start-maximized")
webdriver_path = './chromedriver'

driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
store_info = []
for url in urls:
    driver.get(url)
    width = 3000
    height = 1000
    driver.set_window_size(width, height)
    time.sleep(10)
    product_info = driver.find_element(By.CLASS_NAME, 'slick-track').text.split('\n')
    print(product_info)