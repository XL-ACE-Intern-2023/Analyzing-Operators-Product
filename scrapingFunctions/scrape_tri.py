import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("start-maximized")
webdriver_path = './chromedriver'

driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
main_url = 'https://my.tri.co.id/data'

driver.get(main_url)

time.sleep(5)
products_button = driver.find_elements(By.CLASS_NAME, 'card-body')
for j in range(2, len(products_button), 2):
    while True:
        try:
            products_button[j].click()
            break
        except:
            products_button = driver.find_elements(By.CLASS_NAME, 'card-body')

    time.sleep(5)
    buttons = driver.find_elements(By.CLASS_NAME, 'card-more-btn')
    for i in range(len(buttons)):
        while True:
            try:
                buttons[i].click()
                break
            except:
                buttons = driver.find_elements(By.CLASS_NAME, 'card-more-btn')

        time.sleep(5)
        infos = driver.find_elements(By.CLASS_NAME, 'card-body')
        try:
            for info in infos:
                print(info.text)
        except:
            print(infos.text)
        driver.back()
        break

