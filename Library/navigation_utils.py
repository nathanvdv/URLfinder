import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import re

def login(driver, username, password):
    driver.get("https://kbopub.economie.fgov.be/kbo-open-data/login?lang=nl")
    driver.find_element(By.ID, "j_username").send_keys(username)
    driver.find_element(By.ID, "j_password").send_keys(password)
    driver.find_element(By.ID, "proceed").click()

def navigate_and_download(driver, download_dir):
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Download een KBO Open Data Bestand"))
    ).click()

    links = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "_Full.zip")]'))
    )

    file_dates = {}
    for link in links:
        href = link.get_attribute('href')
        match = re.search(r'(\d{4}_\d{2})_Full\.zip', href)
        if match:
            date_str = match.group(1)
            date = datetime.strptime(date_str, '%Y_%m')
            file_dates[date] = href

    if file_dates:
        latest_date = max(file_dates.keys())
        latest_file_url = file_dates[latest_date]
        latest_file_name = f"{latest_date.strftime('%Y_%m')}_Full.zip"
        if latest_file_name not in os.listdir(download_dir):
            driver.get(latest_file_url)  # This initiates the download
            return True
        else:
            print("Latest file already downloaded.")
            return False
