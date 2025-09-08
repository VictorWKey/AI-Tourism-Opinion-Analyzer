#!/usr/bin/env python3
import subprocess
import sys
import time
from datetime import datetime

def ejecutar_comando(comando):
    """Ejecuta un comando y retorna el código de salida"""
    print(f"\n{'='*80}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ejecutando:")
    print(f"{comando}")
    print('='*80)
    
    try:
        # Ejecutar el comando
        resultado = subprocess.run(comando, shell=True, check=True, 
                                 capture_output=False, text=True)
        print(f"\n✅ Comando completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el comando. Código de salida: {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️ Ejecución interrumpida por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def main():
    # Lista de comandos a ejecutar
    comandos = [
        # Mazatlán
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-malecon-de-mazatlan https://www.tripadvisor.com.mx/Attraction_Review-g150792-d278625-Reviews-Malecon_de_Mazatlan-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-isla-de-la-piedras https://www.tripadvisor.com.mx/Attraction_Review-g150792-d152282-Reviews-Stone_Island_Isla_de_las_Piedras-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-plaza-machado https://www.tripadvisor.com.mx/Attraction_Review-g150792-d153038-Reviews-Plaza_Machado-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-el-faro-de-mazatlan https://www.tripadvisor.com.mx/Attraction_Review-g150792-d152745-Reviews-Faro_Mazatlan-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-playa-brujas https://www.tripadvisor.com.mx/Attraction_Review-g150792-d153039-Reviews-Playa_Brujas-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-viejo-mazatlan https://www.tripadvisor.com.mx/Attraction_Review-g150792-d504405-Reviews-Old_Mazatlan-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-acuario-mazatlan https://www.tripadvisor.com.mx/Attraction_Review-g150792-d152749-Reviews-Gran_Acuario_Mazatlan_Mar_de_Cortes-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-catedral-mazatlan-basilica-de-la-inmaculada-concepcion https://www.tripadvisor.com.mx/Attraction_Review-g150792-d152747-Reviews-Catedral_Mazatlan_Basilica_de_la_Inmaculada_Concepcion-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-isla-de-los-venados https://www.tripadvisor.com.mx/Attraction_Review-g150792-d278610-Reviews-Deer_Island_Isla_de_Venados-Mazatlan_Pacific_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw mazatlan-playa-cerritos https://www.tripadvisor.com.mx/Attraction_Review-g150792-d153743-Reviews-Playa_Cerritos-Mazatlan_Pacific_Coast.html',
        
        # Puebla
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-africam-safari https://www.tripadvisor.com.mx/Attraction_Review-g152773-d2538696-Reviews-Africam_Safari-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-acuario-michin-puebla https://www.tripadvisor.com.mx/Attraction_Review-g152773-d19702785-Reviews-Acuario_Michin_Puebla-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-capilla-del-rosario https://www.tripadvisor.com.mx/Attraction_Review-g152773-d156071-Reviews-Capilla_del_Rosario_Templo_de_Santo_Domingo-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-zoo-parque-loro-puebla https://www.tripadvisor.com.mx/Attraction_Review-g152773-d6002152-Reviews-Zoo_Parque_Loro_Puebla-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-zocalo-de-puebla https://www.tripadvisor.com.mx/Attraction_Review-g152773-d156070-Reviews-Zocalo_de_Puebla-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-callejon-de-los-sapos https://www.tripadvisor.com.mx/Attraction_Review-g152773-d153796-Reviews-Callejon_de_los_Sapos-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-fuertes-de-loreto https://www.tripadvisor.com.mx/Attraction_Review-g152773-d153797-Reviews-Fuertes_de_Loreto-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-museo-internacional-del-barroco https://www.tripadvisor.com.mx/Attraction_Review-g152773-d10043505-Reviews-Museo_Internacional_del_Barroco-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-catedral-de-puebla https://www.tripadvisor.com.mx/Attraction_Review-g152773-d153872-Reviews-Puebla_Cathedra-Puebla_Central_Mexico_and_Gulf_Coast.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puebla-mercado-el-parian https://www.tripadvisor.com.mx/Attraction_Review-g152773-d1157293-Reviews-Mercado_el_Parian-Puebla_Central_Mexico_and_Gulf_Coast.html',
        
        # Puerto Vallarta
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-malecon-boardwalk https://www.tripadvisor.com.mx/Attraction_Review-g150793-d2440853-Reviews-Malecon_Boardwalk-Puerto_Vallarta.HTML',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-zona-romantica https://www.tripadvisor.com.mx/Attraction_Review-g150793-d152509-Reviews-Zona_Romantica-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-parroquia-de-nuestra-señora-de-guadalupe https://www.tripadvisor.com.mx/Attraction_Review-g150793-d313574-Reviews-Parroquia_de_Nuestra_Senora_de_Guadalupe-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-playa-de-los-muertos https://www.tripadvisor.com.mx/Attraction_Review-g150793-d153514-Reviews-Playa_de_los_Muertos-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-marina-vallarta https://www.tripadvisor.com.mx/Attraction_Review-g150793-d152496-Reviews-Marina_Vallarta-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-playa-de-las-gemelas https://www.tripadvisor.com.mx/Attraction_Review-g150793-d2232380-Reviews-Playa_Las_Gemelas-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-bahia-de-banderas https://www.tripadvisor.com.mx/Attraction_Review-g150793-d152293-Reviews-Bay_of_Banderas-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-san-pancho https://www.tripadvisor.com.mx/Attraction_Review-g150793-d12652212-Reviews-San_Pancho-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-mirador-de-la-cruz https://www.tripadvisor.com.mx/Attraction_Review-g150793-d10756317-Reviews-Mirador_de_La_Cruz-Puerto_Vallarta.html',
        'python scripts/recoleccion/web_scrapping_avanzado.py ./data/raw puerto-vallarta-edenva-parque-ecoturistico https://www.tripadvisor.com.mx/Attraction_Review-g1015495-d153492-Reviews-Edenva_Parque_Ecoturistico-Mismaloya_Puerto_Vallarta.html'
    ]
    
    print("🚀 Iniciando ejecución de comandos de web scraping")
    print(f"Total de comandos: {len(comandos)}")
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    inicio_total = time.time()
    exitosos = 0
    fallidos = 0
    
    for i, comando in enumerate(comandos, 1):
        print(f"\n📝 Progreso: {i}/{len(comandos)}")
        
        inicio_comando = time.time()
        if ejecutar_comando(comando):
            exitosos += 1
        else:
            fallidos += 1
            # Preguntar si continuar después de un error
            respuesta = input("\n❓ ¿Deseas continuar con el siguiente comando? (s/n): ")
            if respuesta.lower() not in ['s', 'si', 'y', 'yes']:
                print("🛑 Ejecución detenida por el usuario")
                break
        
        tiempo_comando = time.time() - inicio_comando
        print(f"⏱️ Tiempo del comando: {tiempo_comando:.2f} segundos")
        
        # Pequeña pausa entre comandos para evitar sobrecarga
        if i < len(comandos):
            print("⏳ Pausa de 2 segundos antes del siguiente comando...")
            time.sleep(2)
    
    # Resumen final
    tiempo_total = time.time() - inicio_total
    print(f"\n{'='*80}")
    print("📊 RESUMEN DE EJECUCIÓN")
    print('='*80)
    print(f"✅ Comandos exitosos: {exitosos}")
    print(f"❌ Comandos fallidos: {fallidos}")
    print(f"📝 Total ejecutados: {exitosos + fallidos}")
    print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos ({tiempo_total/60:.1f} minutos)")
    print(f"🏁 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if fallidos > 0:
        print(f"\n⚠️ Se encontraron {fallidos} errores durante la ejecución")
        return 1
    else:
        print(f"\n🎉 Todos los comandos se ejecutaron exitosamente")
        return 0

if __name__ == "__main__":
    sys.exit(main())