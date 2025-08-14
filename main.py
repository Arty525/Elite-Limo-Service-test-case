import time

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait


# Настройка Selenium (например, для Chrome)
base_url = "https://www.partyslate.com"
chrome_options = Options()
prefs = {
    "profile.managed_default_content_settings.images": 2,  # Разрешаем картинки
    "profile.managed_default_content_settings.video": 2,   # Блокируем видео (2 = блок)
    "profile.managed_default_content_settings.audio": 2,    # Блокируем аудио
    "profile.default_content_setting_values.media_stream": 2,  # Блокируем запросы камеры/микрофона
}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)
driver.get(base_url + "/find-vendors/event-planner/area/miami")

# Ждём загрузки JS
time.sleep(3)

# Получаем HTML после выполнения JS
html = driver.page_source

#print(html)
soup = BeautifulSoup(html, 'html.parser')

# Далее парсим с помощью BeautifulSoup
data = soup.find_all("h3", class_="src-components-CompanyDirectoryCard-components-Header-Header-module__title__2okBV")
# with open("site_data.txt", "w") as f:
#     for item in data:
#         f.write(f"{str(item)}\n")

results = {}
for item in data:
    results[item.text] = {"url" : item.find("a").get("href"), "staff": []}

for result in results:
    print(results[result])

for result in results:
    url = base_url + results[result]["url"]
    driver.get(url)
    print(result)
    try:
        while True:
            # Ждём, пока кнопка "Далее" станет кликабельной
            next_button = driver.find_element(
                By.XPATH,
                "//button[@aria-label='view next team member' and not(@disabled)]"
            )
            # next_button = driver.find_element(
            #     By.XPATH,
            #     "//button[@aria-label='view next team member']"
            # )

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            # Получаем текущие данные со слайдера
            staff = soup.find("h3",
                                 class_="css-1ham2m0")
            position = soup.find("span", class_="css-1pxun7d")
            results[result]["staff"].append({"full_name": staff.text, "position": position.text})

            # Кликаем "Далее"
            driver.execute_script("arguments[0].click();", next_button)

            # Ждём обновления контента (можно настроить точное ожидание)
            time.sleep(1)
    except NoSuchElementException:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        staff = soup.find("h3",
                             class_="css-1ham2m0")
        position = soup.find("span", class_="css-1pxun7d")
        if staff is not None:
            results[result]["staff"].append({"full_name": staff.text, "position": position.text})
        else:
            results[result]["staff"].append({"full_name": "", "position": ""})

for result in results:
    print(result)
    for person in results[result]["staff"]:
        print(f"{person["full_name"]} ({person["position"]})")
    print("==================")

driver.quit()  # Закрываем браузер
