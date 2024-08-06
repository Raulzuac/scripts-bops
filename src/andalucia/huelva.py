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

def fetch_huelva_data():
    #fecha
    date = datetime.date.today().strftime('%d-%m-%Y')
    #Configuración de ssl necesaria para poder cargar la página
    ssl._create_default_https_context = ssl._create_stdlib_context

    #Abrimos la página del bop de huelva
    url = 'https://s2.diphuelva.es/servicios/bope_web/UltimoBop'
    #Procesamos el contenido de la página
   
    browser = webdriver.Firefox()
    browser.get(url)
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hijo"))
        )
        #BOP número. 144: 24/07/2024 > 144
        
    finally:
        number = element.text.split(':')[0].split(' ')[2]
        browser.quit()
    
    #Descargamos el pdf¡
    year = datetime.date.today().year
    url_pdf = f'https://s2.diphuelva.es/portalweb/bope/anuncios/IndiceBOP_{number}_{year}.pdf'
    #Descargamos el archivo pdf
    request = requests.get(url_pdf)
    with open(f'src/andalucia/pdfs/huelva_{date}.pdf', 'wb') as f:
        f.write(request.content)
    
    #Guardamos el archivo y el contenido en la base de datos
    try:
        con = mariadb.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=3306,
            database="bops"
        )
        id = str(ULID())
        with open(f'src/andalucia/pdfs/huelva_{date}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (place,date,id,file) VALUES (?,?,?,?)", ('BOP Huelva',datetime.date.today(),id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/huelva_{date}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (bopId,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
        
        con.commit()

        os.remove(f'src/andalucia/pdfs/huelva_{date}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")