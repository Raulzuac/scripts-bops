from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os

def fetch_cadiz_data():
    date = datetime.date.today().strftime('%d-%m-%Y')
    url = 'https://www.bopcadiz.es'
    response = requests.get(url)
    html = response.text
    #buscamos las etiquetas a
    labels = re.findall(r"<[^>]+>", html)
    for label in labels:
        if('bopcadiz' in label):
            url_pdf = re.findall(r"href=\"(.+)\" ", label)[0]
            break
    request = requests.get(url_pdf)
    with open(f'src/andalucia/pdfs/cadiz_{date}.pdf', 'wb') as f:
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
        with open(f'src/andalucia/pdfs/cadiz_{date}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (id,file) VALUES (?,?)", (id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/cadiz_{date}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (id_bop,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
        
        con.commit()

        os.remove(f'src/andalucia/pdfs/cadiz_{date}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")