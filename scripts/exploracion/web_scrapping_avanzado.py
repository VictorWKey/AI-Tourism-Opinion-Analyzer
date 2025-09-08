#!/usr/bin/env python
# %%
import urllib
import urllib.request
from urllib.parse import urlparse
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
import csv
import math
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def verify_soup_variable(soup):
    if bool(soup):
        text = soup.get_text()
    else:
        text = ""
    return text

# %% PAGINA PRINCIPAL https://www.tripadvisor.com.mx/Attraction_Review-g150804-d5114009-Reviews-Chachalacas_Beach-Veracruz_Central_Mexico_and_Gulf_Coast.html
urlcompleta = r"" + sys.argv[3]
URL_main_part1 = r'https://www.tripadvisor.com.mx/Attraction_Review'
URL_main_part2 = urlcompleta.replace(URL_main_part1, "")

output_path = os.getcwd() + r"/" + sys.argv[1]
output_file_name = f"{sys.argv[2]}.csv"

overwrite = True

# %%
cont = 0
page_number = 1
opiniones_recopiladas = 0  # Contador de opiniones recopiladas
max_opiniones = 50  # Límite de opiniones a recopilar

if overwrite == True:
    output_file = open(output_path + "/" + output_file_name, "w", encoding="utf-8")
else:
    output_file = open(output_path + "/" + output_file_name, "a", encoding="utf-8")

cvs = csv.writer(output_file)

if os.path.exists(output_path + "/" + output_file_name):
    if os.stat(output_path + "/" + output_file_name).st_size == 0:
        cvs.writerow(["Titulo", "Review", "TipoViaje", "Calificacion", "OrigenAutor", "FechaOpinion", "FechaEstadia"])

band_page = 0

# Configuración de Playwright
with sync_playwright() as p:
    # Iniciar el navegador (cambiar a headless=True en producción)
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    )
    
    # Bloquear popups y modals molestos
    context.route("**/*", lambda route: route.abort() if "braze" in route.request.url or "modal" in route.request.url else route.continue_())
    
    page = context.new_page()

    # Primera navegación a la página principal para establecer cookies
    try:
        page.goto('https://www.tripadvisor.com.mx/', wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(2000)  # Espera como humano
    except PlaywrightTimeoutError:
        print("Timeout al cargar la página principal, continuando de todos modos...")

    # Bandera para controlar si ya se hizo clic en "Mostrar opiniones traducidas"
    # Cambiamos a False para verificar en cada página
    traducidas_clicked = False

    while cont < page_number and opiniones_recopiladas < max_opiniones:
        if cont > 50:
            break

        if cont == 0:
            URL = URL_main_part1 + URL_main_part2
        else:
            URL = URL_main_part1 + '-or' + str(cont * 10) + URL_main_part2

        print(f"Intentando acceder a: {URL}")

        try:
            # Navegar a la página de reseñas
            page.goto(URL, wait_until='domcontentloaded', timeout=60000)

            # Esperar a que carguen las reseñas
            page.wait_for_selector('.eSDnY', timeout=30000)

            # VERIFICAR Y ACTIVAR "Mostrar opiniones originales" EN CADA PÁGINA
            try:
                # Esperar un poco para que la página se cargue
                page.wait_for_timeout(2000)
                
                # Buscar específicamente el botón que contiene "Mostrar opiniones originales"
                try:
                    # Intentar encontrar el botón por su texto específico
                    traducidas_button = page.get_by_role("button", name="Mostrar opiniones originales")
                    button_count = traducidas_button.count()
                    
                    if button_count > 0:
                        print(f"🔄 Página {cont}: Activando 'Mostrar opiniones originales'")
                        
                        # Scroll rápido hacia el botón
                        page.evaluate("window.scrollBy(0, 150)")
                        page.wait_for_timeout(500)
                        
                        # Clic directo sin tanto delay
                        traducidas_button.first.click()
                        page.wait_for_timeout(2000)  # Solo 2 segundos de espera
                        
                        print("✅ Opiniones originales activadas")
                        
                    else:
                        # Verificar si ya están en original
                        traducidas_alt_button = page.get_by_role("button", name="Mostrar opiniones traducidas")
                        if traducidas_alt_button.count() > 0:
                            print(f"✅ Página {cont}: Opiniones ya están en idioma original")
                        else:
                            print(f"⚠️ Página {cont}: No se encontró botón de idioma")
                        
                except Exception as selector_error:
                    print(f"🔧 Página {cont}: Usando método alternativo...")
                    
                    # Método alternativo más rápido
                    button_selector = "button.rmyCe._G.B-.z._S.c.Wc.wSSLS.jWkoZ.sOtnj"
                    all_buttons = page.locator(button_selector)
                    
                    found_button = False
                    for i in range(min(all_buttons.count(), 5)):  # Limitar a 5 botones máximo
                        try:
                            button_text = all_buttons.nth(i).locator("span").text_content()
                            if "Mostrar opiniones originales" in button_text:
                                print(f"✅ Página {cont}: Botón encontrado en posición {i}")
                                all_buttons.nth(i).click()
                                page.wait_for_timeout(1500)
                                found_button = True
                                break
                        except Exception:
                            continue
                    
                    if not found_button:
                        print(f"ℹ️ Página {cont}: Asumiendo que ya están en idioma original")
                        
            except Exception as e:
                print(f"⚠️ Página {cont}: Error al verificar idioma: {e}")

            # Esperar un poco más para que se actualicen las opiniones
            page.wait_for_timeout(1000)

            # Obtener el contenido HTML
            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            # Obtenemos el div donde están los comentarios
            review_section = soup.find_all(class_='eSDnY')[0]

            if band_page == 0:
                # Obtener el número total de reseñas
                ld_json_scripts = soup.find_all('script', type='application/ld+json')
                if ld_json_scripts:
                    SRevCount = str(ld_json_scripts[-1])
                    SRevCount = SRevCount.replace('<script type="application/ld+json">', '')
                    SRevCount = SRevCount.replace('</script>', '')
                    try:
                        RevCount = json.loads(SRevCount)
                        num_reviews_text_ = RevCount['aggregateRating']['reviewCount']
                        total_reviews = int(num_reviews_text_)
                        page_number = int(math.ceil(total_reviews / 10))
                        band_page = 1
                        print(f"Total de reseñas: {total_reviews}, Páginas: {page_number}")
                    except (KeyError, json.JSONDecodeError) as e:
                        print(f"Error al procesar JSON-LD: {e}")
                        # Valor por defecto si no podemos obtener el número de páginas
                        page_number = 10

            cont = cont + 1
            print("******", cont, " de ", page_number, f" | Opiniones recopiladas: {opiniones_recopiladas}/{max_opiniones}")

            reviews = []
            for g in review_section.find_all(class_='_c'):
                # Verificar si ya llegamos al límite antes de procesar la opinión
                if opiniones_recopiladas >= max_opiniones:
                    print(f"🎯 Límite alcanzado: {max_opiniones} opiniones recopiladas")
                    break
                    
                titulo = verify_soup_variable(g.find(class_='yCeTE'))
                review = verify_soup_variable(g.find(class_='biGQs _P VImYz AWdfh'))

                # Extraer calificación
                score_element = g.find(class_='evwcZ')
                if score_element and score_element.find('title'):
                    data = score_element.find('title').text
                    data = data.split(' ')
                    score = data[0]
                else:
                    score = "N/A"

                aportes = verify_soup_variable(g.find(class_='IugUm'))
                if aportes == '':
                    origen = ''
                else:
                    origen_el = g.find(class_='biGQs _P navcl')
                    if origen_el:
                        origen = origen_el.get_text().replace(aportes, "")
                    else:
                        origen = ""

                fecha_estadia_el = g.find(class_="RpeCd")
                if fecha_estadia_el:
                    fecha_estadia_ = verify_soup_variable(fecha_estadia_el).split("•")
                    fecha_estadia = fecha_estadia_[0].strip() if fecha_estadia_ else ""
                    if fecha_estadia and ',' in fecha_estadia:
                        tipoViaje = fecha_estadia_[1].split(",")[0] if len(fecha_estadia_) > 1 else ""
                    else:
                        tipoViaje = ""
                else:
                    fecha_estadia = ""
                    tipoViaje = ""

                fecha_opinion_el = g.find(class_="biGQs _P pZUbB ncFvv navcl")
                if fecha_opinion_el:
                    fecha_opinion = verify_soup_variable(fecha_opinion_el).replace("Escrita el ", "")
                else:
                    fecha_opinion = ""

                print([titulo, review, tipoViaje, score, origen, fecha_opinion, fecha_estadia])
                cvs.writerow([titulo, review, tipoViaje, score, origen, fecha_opinion, fecha_estadia])

                # Incrementar contador de opiniones recopiladas
                opiniones_recopiladas += 1
                print(f"📝 Opinión {opiniones_recopiladas}/{max_opiniones} guardada")

                # Micro sleep between reviews (reducido)
                time.sleep(random.uniform(0.2, 0.8))

            # Verificar si ya alcanzamos el límite después del for
            if opiniones_recopiladas >= max_opiniones:
                print(f"🏁 Proceso completado: {opiniones_recopiladas} opiniones recopiladas")
                break

            # Espera entre páginas (reducida)
            time.sleep(random.uniform(1.0, 2.0))

        except PlaywrightTimeoutError:
            print(f"Timeout al cargar la página {cont}. Saltando a la siguiente...")
            cont += 1
        except Exception as e:
            print(f"Error inesperado: {e}")
            # Intenta continuar con la siguiente página
            cont += 1

    # Cerrar el navegador
    browser.close()

output_file.close()
print(f"🎉 Extracción completada. Total de opiniones recopiladas: {opiniones_recopiladas}")
print(f"📁 Archivo guardado: {output_path}/{output_file_name}")
