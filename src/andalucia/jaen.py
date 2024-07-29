from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os

def fetch_jaen_data():
    #Calculamos la fecha del día de hoy
    date = datetime.date.today().strftime('%d-%m-%Y')
    url = f'https://bop.dipujaen.es/bop/{date}'
    #Cargamos la página
    pageBop = urlopen(url)
    #Leemos el contenido de la página
    html_bytes = pageBop.read()
    html = html_bytes.decode("latin-1")
    #Buscamos la url del archivo pdf
    urlArchivo = ""
    #Separamos las etiquetas html
    labels = re.findall(r"<[^>]+>", html)
    #Buscamos la etiqueta que contiene la url del archivo pdf
    for label in labels:
        if("bopCompleto" in label):
            for value in label.split(' '):
                if("href" in value):
                    fileurl = re.findall(r"='(.+)'", value)[0].replace("'", "")
                    break

    #Descargamos el archivo pdf
    request = requests.get(fileurl)
    with open(f'src/andalucia/pdfs/jaen_{date}.pdf', 'wb') as f:
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
        with open(f'src/andalucia/pdfs/jaen_{date}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (id,file) VALUES (?,?)", (id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/jaen_{date}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (id_bop,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
        
        con.commit()

        os.remove(f'src/andalucia/pdfs/jaen_{date}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")