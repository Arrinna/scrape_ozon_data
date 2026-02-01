import time
import os
import glob
import undetected_chromedriver as uc

# Папка для загрузки файлов
DOWNLOAD_DIR = r"C:\Users\USER\Downloads"
USER_DATA_DIR = r'C:\Users\USER\ozon_temp_profile'
PROFILE_DIR = 'Default'

# Настройки undetected-chromedriver
options = uc.ChromeOptions()
options.add_argument(f'--user-data-dir={USER_DATA_DIR}')
options.add_argument(f'--profile-directory={PROFILE_DIR}')
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Чтение ссылок и лейблов из ozon_links.csv
links = []
with open("ozon_links.csv", encoding="utf-8") as f:
    next(f)  # пропустить заголовок
    for line in f:
        parts = line.rstrip().split(";")
        if len(parts) == 2:
            label, url = parts
            links.append((label, url))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Вспомогательная функция для поиска последнего скачанного файла
def get_latest_downloaded_file(download_dir):
    files = glob.glob(os.path.join(download_dir, '*'))
    if not files:
        return None
    return max(files, key=os.path.getctime)

# Запуск браузера через undetected-chromedriver
with uc.Chrome(options=options) as driver:
    for label, url in links:
        try:
            driver.get(url)
            time.sleep(2)  # дать странице прогрузиться, можно увеличить
            wait = WebDriverWait(driver, 20)
            download_btn = None
            
            # 1. Пробуем найти по XPATH (старый способ)
            try:
                download_btn = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[.//div[text()='Download']]"
                    ))
                )
            except Exception:
                pass

            # 2. Если не нашли, пробуем по CSS и тексту
            if not download_btn:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, "button.ozi__button__button__nNN_g")
                    for btn in buttons:
                        try:
                            text_div = btn.find_element(By.CSS_SELECTOR, ".ozi__button__text__nNN_g")
                            if text_div.text.strip() == "Download":
                                download_btn = btn
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

            # 3. Если не нашли, пробуем по полному XPath
            if not download_btn:
                try:
                    download_btn = wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "/html/body/div[1]/div/div/div[2]/div/div[3]/div[2]/button"
                        ))
                    )
                except Exception:
                    pass

            # 4. Если не нашли, сохраняем скриншот и HTML для диагностики
            if not download_btn:
                ts = int(time.time())
                driver.save_screenshot(f'screenshot_{ts}.png')
                with open(f'page_{ts}.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                raise Exception("Download button not found. Screenshot and HTML saved.")
            # Кликаем по кнопке
            before_files = set(os.listdir(DOWNLOAD_DIR))
            download_btn.click()
            print(f"Clicked Download on: {url}")

            # Ждём появления нового файла
            downloaded_file = None
            for _ in range(60):  # до 60 секунд
                time.sleep(1)
                after_files = set(os.listdir(DOWNLOAD_DIR))
                new_files = after_files - before_files
                if new_files:
                    # Берём первый новый файл
                    downloaded_file = os.path.join(DOWNLOAD_DIR, list(new_files)[0])
                    # Проверяем, что файл не .crdownload
                    if not downloaded_file.endswith('.crdownload'):
                        break
            if not downloaded_file or downloaded_file.endswith('.crdownload'):
                print(f"Warning: Downloaded file for {label} not found or still downloading.")
                continue

            # Переименовываем файл
            new_name = os.path.join(DOWNLOAD_DIR, f"{label}.xlsx")

            # Если файл с таким именем уже есть, удаляем
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(downloaded_file, new_name)
            print(f"Saved as: {new_name}")

        except Exception as e:
            print(f"Error on {url}: {e}")
