from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os
import ssl

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def fetch_cordoba_data():
    ssl._create_default_https_context = ssl._create_stdlib_context

    print('Descargando datos de cordoba....')
    url = 'https://bop.dipucordoba.es'
    date = datetime.date.today().strftime('%d-%m-%Y')
    
    browser = webdriver.Firefox()
    browser.get(url)
    try:
        elements = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )
        
    finally:
        for element in elements:
            if('BOP-S-2024' in element.text):
                #Sum. BOP-S-2024-143 > 143
                number = element.text.split('-')[3]
                break
        
    browser.quit()
    url_pdf = f'https://bop.dipucordoba.es/visor-pdf/{date}/BOP-S-{datetime.date.today().year}-{number}.pdf'
    #Descargamos el archivo pdf
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

# Use urllib to open the URL and read the content
    pdf_response = urlopen(url_pdf, context=ctx)
    with open(f'src/andalucia/pdfs/cordoba_{date}.pdf', 'wb') as f:
        f.write(pdf_response.read())

    try:
        con = mariadb.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=3306,
            database="bops"
        )
        id = str(ULID())
        with open(f'src/andalucia/pdfs/cordoba_{date}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (id,file) VALUES (?,?)", (id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/cordoba_{date}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (id_bop,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
        
        con.commit()

        os.remove(f'src/andalucia/pdfs/cordoba_{date}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")
    # browser.quit()
    # print(response.text)