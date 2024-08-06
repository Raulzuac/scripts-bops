from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os

def fetch_almeria_data():
    url = 'https://www.dipalme.org/Servicios/cmsdipro/index.nsf/bop_view.xsp?p=dipalme'
    response = requests.get(url)
    html = response.text
    #buscamos las etiquetas a
    labels = re.findall(r"<[^>]+>", html)
    for label in labels:
        if('bopanexos' in label):
            pdf_name = re.findall(r"href=(.+) title", label)[0]
            break
    url_pdf = f'https://www.dipalme.org{pdf_name}'

    request = requests.get(url_pdf)
    date = datetime.date.today().strftime('%d-%m-%Y')
    with open(f'src/andalucia/pdfs/almeria_{date}.pdf', 'wb') as f:
        f.write(request.content)

    try:
        con = mariadb.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port=3306,
            database="bops"
        )
        id = str(ULID())
        with open(f'src/andalucia/pdfs/almeria_{date}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (place,date,id,file) VALUES (?,?,?,?)", ('BOP Almería',datetime.date.today(),id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/almeria_{date}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (bopId,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
        
        con.commit()

        os.remove(f'src/andalucia/pdfs/almeria_{date}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")