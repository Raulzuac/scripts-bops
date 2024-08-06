from andalucia.almeria import fetch_almeria_data
from andalucia.cadiz import fetch_cadiz_data
from andalucia.cordoba import fetch_cordoba_data
from andalucia.granada import fetch_granada_data
from andalucia.huelva import fetch_huelva_data
from andalucia.jaen import fetch_jaen_data
from andalucia.malaga import fetch_malaga_data
from andalucia.sevilla import fetch_sevilla_data

def fetch_data_andalucia():
    #LLamadas a las funciones de cada provincia
    fetch_almeria_data()
    fetch_cadiz_data()
    fetch_cordoba_data()
    fetch_granada_data()
    fetch_huelva_data()
    fetch_jaen_data()
    # fetch_malaga_data()
    fetch_sevilla_data()

    #Buscamos los datos de la propia andalucía en general
    print("Datos de andalucía")