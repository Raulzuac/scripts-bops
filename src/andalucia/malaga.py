from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os
import shutil

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def fetch_malaga_data():
    url_download = 'C:/Users/Zucar/Downalods'
    url = 'https://www.bopmalaga.es/sumario.php'
    date = datetime.date.today().strftime('%d-%m-%Y')
    browser = webdriver.Firefox()
    browser.get(url)
    elements = browser.find_elements(By.TAG_NAME, 'a')
    for element in elements:
        if('Boletín nº' in element.text):
            # Boletín nº 144 en pdf > 144
            number = element.text.split(' ')[2]
            # element.click()
            break
    browser.quit()
    #25072024 > 250724
    date_no_sapce = datetime.date.today().strftime('%d%m%y')
    datenumber = date_no_sapce[:4] + date_no_sapce[4:]

    
    filename = f'{datenumber}{number}.pdf'
    source = f'{url_download}/{filename}'
    destiny = f'src/andalucia/pdfs/malaga_{date}.pdf'
    shutil.move(source, destiny)