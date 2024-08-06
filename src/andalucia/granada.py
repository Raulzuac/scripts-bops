from ulid import ULID
from urllib.request import urlopen
from PyPDF2 import PdfReader
import re
import requests
import mariadb
import datetime
import os
import ssl

def fetch_granada_data():
    #Configuración de ssl necesaria para poder cargar la página
    ssl._create_default_https_context = ssl._create_stdlib_context
    print('Cargando cosas de granada............')
    #Calculamos la url con el día de hoy
    date = datetime.date.today().strftime('%d/%m/%Y')
    url = f'https://bop2.dipgra.es/opencms/opencms/portal/index.jsp?opcion=listaEventos&fecha={date}'
    #Cargamos la página
    pageBop = urlopen(url)
    html_bytes = pageBop.read()
    html = html_bytes.decode("latin-1")
    filename = f'bop-{date.replace("/","_")}'
    #Buscamos la url del archivo pdf
    labels = re.findall(r"<[^>]+>", html)
    for label in labels:
        if(filename in label):
            for value in label.split(' '):
                if("href" in value):
                    fileurl = re.findall(r"=\"(.+)\"", value)[0].replace("'", "")
                    break
    print(f'https://bop.dipgra.es{fileurl}')
    request = requests.get(f'https://bop.dipgra.es{fileurl}',verify=False)
    with open(f'src/andalucia/pdfs/granada_{date.replace('/','-')}.pdf', 'wb') as f:
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
        with open(f'src/andalucia/pdfs/granada_{date.replace('/','-')}.pdf', 'rb') as f:
            pdf = f.read()
            cur = con.cursor()
            cur.execute("INSERT INTO bops (place,date,id,file) VALUES (?,?,?,?)", ('BOP Granada',datetime.date.today(),id,pdf))

        reader = PdfReader(f'src/andalucia/pdfs/granada_{date.replace('/','-')}.pdf')
        counter = 0
        for page in reader.pages:
            counter += 1
            cur.execute("INSERT INTO pages (bopId,num_page,content) VALUES (?,?,?)", (id,counter,page.extract_text()))
            print(f'Guardando página {counter} de granada')
        con.commit()

        os.remove(f'src/andalucia/pdfs/granada_{date.replace('/','-')}.pdf')
    except mariadb.Error as e:
        print(f"Error: {e}")