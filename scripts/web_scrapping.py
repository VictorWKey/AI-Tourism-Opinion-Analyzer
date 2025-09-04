"""Extrae información relevante de un review de TripAdvisor.

    Returns:
        dict: Un diccionario con la información extraída del review.
        
    Uso: 
        cd /home/victorwkey/analisis-automatizado-de-opiniones-turisticas && python web_scrapping.py data cdmx-01-test https://www.tripadvisor.com.mx/Attraction_Review-g150800-d153711-Reviews-or10-Museo_Nacional_de_Antropologia-Mexico_City_Central_Mexico_and_Gulf_Coast.html 2>&1 | head -50
"""


#!/usr/bin/env python
# %%
import urllib
import urllib.request
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import datetime
from pathlib import Path
import errno
import random
import pandas as pd
import numpy as np
import sys
import json
import os
import time
import csv
import math

# Create a session for better connection handling
session = requests.Session()

# More comprehensive headers to avoid detection
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

session.headers.update(headers)

def warm_up_session():
    """Visit TripAdvisor homepage first to establish session"""
    try:
        print("Warming up session...")
        resp = session.get("https://www.tripadvisor.com.mx/", timeout=30)
        time.sleep(random.uniform(2.0, 5.0))
        return resp.status_code == 200
    except:
        return False


def verify_soup_variable(soup):
    if bool(soup):
        text = soup.get_text()
    else:
        text=""

    return text

# %% PAGINA PRINCIPAL https://www.tripadvisor.com.mx/Attraction_Review-g150804-d5114009-Reviews-Chachalacas_Beach-Veracruz_Central_Mexico_and_Gulf_Coast.html
urlcompleta = r""+sys.argv[3]
URL_main_part1 = r'https://www.tripadvisor.com.mx/Attraction_Review'
URL_main_part2 = urlcompleta.replace(URL_main_part1,"")

output_path = os.getcwd()+r"/"+sys.argv[1]
output_file_name=f"{sys.argv[2]}.csv"

overwrite = True
#https://www.tripadvisor.com.mx/Hotel_Review-g154267-d283703-Reviews-or5-Grand_Velas_Riviera_Nayarit-Nuevo_Vallarta_Pacific_Coast.html#REVIEWS


# %%
cont = 0
page_number = 1
if overwrite ==True:
    output_file = open(output_path + "/" + output_file_name, "w",encoding="utf-8")
else:
    output_file = open(output_path + "/" + output_file_name, "a", encoding="utf-8")

cvs = csv.writer(output_file)

if os.path.exists(output_path + "/" + output_file_name):
    if os.stat(output_path + "/" + output_file_name).st_size==0:
        cvs.writerow(["Titulo", "Review","TipoViaje", "Calificacion", "OrigenAutor", "FechaOpinion", "FechaEstadia"])

# Warm up the session before starting scraping
if not warm_up_session():
    print("Failed to establish initial session. Continuing anyway...")

band_page = 0
while cont < page_number:

    if cont > 50:
        break

    if cont == 0:
        URL = URL_main_part1+URL_main_part2
    else:
        URL = URL_main_part1+'-or'+str(cont*10)+URL_main_part2

    #print(URL)
    
    # Add retry logic and longer delays
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay before request
            time.sleep(random.uniform(3.0, 8.0))
            
            # Use session for better connection handling
            resp = session.get(URL, timeout=30)
            
            if resp.status_code == 200:
                break
            elif resp.status_code == 403:
                print(f"Attempt {attempt + 1}: 403 Forbidden. Waiting longer...")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(10.0, 20.0))
                else:
                    print("Max retries reached. TripAdvisor is blocking requests.")
                    print("Consider:")
                    print("1. Using a VPN")
                    print("2. Waiting longer between requests")
                    print("3. Using different IP addresses")
                    exit()
            else:
                print(f"Attempt {attempt + 1}: Status code {resp.status_code}")
                if attempt == max_retries - 1:
                    exit()
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                exit()
            time.sleep(random.uniform(5.0, 10.0))

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")

        # Obtenemos el div donde estan los comentarios
        review_section = soup.find_all(class_='eSDnY')[0]

        if band_page == 0:
            #num = soup.find_all("a",class_='pageNum')
            #page_number = int(num[len(num)-1].get_text())
            ld_json_scripts = soup.find_all('script', type='application/ld+json')
            SRevCount = str(ld_json_scripts[-1])
            SRevCount = SRevCount.replace('<script type="application/ld+json">','')
            SRevCount = SRevCount.replace('</script>','')
            RevCount  = json.loads(SRevCount)
            #num_reviews_text = review_section.find_all(class_='Ci')[0].get_text()
            num_reviews_text_= RevCount['aggregateRating']['reviewCount'] #num_reviews_text.split()
            total_reviews = int(num_reviews_text_)#int(num_reviews_text_[len(num_reviews_text_)-1].replace(",",""))
            page_number = int(math.ceil(total_reviews/10))
            band_page = 1

        cont = cont + 1
        print("******",cont," de ",page_number)
        reviews = []
        for g in review_section.find_all(class_='_c'):#, recursive=True):

            # Título - selector correcto
            titulo_element = g.find(class_='biGQs _P SewaP qWPrE ncFvv ezezH')
            if titulo_element:
                titulo_span = titulo_element.find(class_='yCeTE')
                titulo = titulo_span.get_text().strip() if titulo_span else ""
            else:
                titulo = ""
            
            # Texto del review - selector correcto
            review_element = g.find(class_='biGQs _P VImYz AWdfh')
            if review_element:
                review_span = review_element.find(class_='yCeTE')
                review = review_span.get_text().strip() if review_span else ""
            else:
                review = ""
            
            # Handle rating with error checking
            data_element = g.find(class_='evwcZ')
            if data_element and data_element.find('title'):
                data = data_element.find('title').text
                # Extraer solo el número de la calificación
                if 'de 5 burbujas' in data:
                    score = data.split()[0]
                else:
                    score = data.split(' ')[0] if data.split(' ') else ''
            else:
                score = ''




            # Información del autor - selector correcto
            autor_element = g.find(class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
            autor_nombre = autor_element.get_text().strip() if autor_element else ""
            
            # Ubicación del autor
            ubicacion_element = g.find('span', string=lambda text: text and 'México' in text or 'Argentina' in text or 'España' in text or 'Colombia' in text)
            if not ubicacion_element:
                # Buscar en el contenedor de información del autor
                info_container = g.find(class_='biGQs _P navcl')
                if info_container:
                    spans = info_container.find_all('span')
                    for span in spans:
                        text = span.get_text().strip()
                        if not 'aportes' in text and len(text) > 3:
                            ubicacion_element = span
                            break
            
            origen = ubicacion_element.get_text().strip() if ubicacion_element else autor_nombre

            #origen = origen.split("•")
            #origen=origen[0]

            fecha_estadia_element = g.find(class_="RpeCd")
            if fecha_estadia_element:
                fecha_estadia_ = fecha_estadia_element.get_text().split("•")
                fecha_estadia = fecha_estadia_[0].strip()
            # Extraer tipo de viaje de la información de estadía
            if len(fecha_estadia_) > 1:
                tipoViaje = fecha_estadia_[1].strip()
            else:
                tipoViaje = ""
            
            # Fecha de opinión - selector correcto
            fecha_opinion_element = g.find(class_="biGQs _P VImYz ncFvv navcl")
            if fecha_opinion_element:
                fecha_opinion = fecha_opinion_element.get_text().replace("Escrita el ", "").strip()
            else:
                fecha_opinion = ""
            
            #author = verify_soup_variable(g.find(class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS'))
            print(f"Título: {titulo[:50]}...")
            print(f"Review: {review[:50]}...")
            print(f"Autor: {origen}")
            print(f"Fecha: {fecha_opinion}")
            print(f"Tipo: {tipoViaje}")
            print(f"Score: {score}")
            print("-" * 50)
            
            cvs.writerow([titulo, review,tipoViaje,score, origen, fecha_opinion, fecha_estadia])
            
        # Longer micro sleep between processing reviews
        time.sleep(random.uniform(0.5, 1.5))
        
        # Longer sleep between pages to avoid detection
        print(f"Waiting before next page...")
        time.sleep(random.uniform(8.0, 15.0))


    else:
        print(f"Status code {resp.status_code}")
        exit()



output_file.close()

# %%
