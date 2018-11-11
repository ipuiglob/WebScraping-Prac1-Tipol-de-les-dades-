########################################################################################################################
#Importem les llibreries necessaries per al nostre codi
import requests
import pandas as pd
import csv
import time
import sys
import datetime
from xml.dom import minidom
from bs4 import BeautifulSoup

#Utilitzarem una funcio a on el parametre sera la URL a fer web scraping
#En aquesta funcio treballarem els conceptes vistos al materia dodent com son:
#el tractament de error, espaiat en la descarrega, modificar user agent
def obtenir_dades(nom_parc,url_pagina):

    #Modifiquem les capceleres i l'user agent per evitar ser bloqueixats.
    # Hi ha la possibilitat en Python de generar user agent de forma aleatoria amb:
    #ua=UserAgent()
    #requests.get("http://forecast.weather.gov/MapClick.php?lat=37.7772&lon=-122.4168", headers={'user-agent': ua.random})
    capcelera = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\*/*;q=0.8", "Accept-Encoding": "gzip, deflate, sdch, br", "Accept-Language": "en-US,en;q=0.8", "Cache-Control": "no-cache", "dnt": "1", "Pragma": "no-cache", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    #Configurem l espaiat de descarrega per a no collapsar la pagina
    t0 = time.time()

    #Codi per al tractament dels errors que es derivin de la execucio del codi (Timeouts, pagina inaccesible)
    try:

        #Descarrega de la pagina web amb les previsions per a una localitat; atencio als parametres de capcalera i timeouts
        pagina = requests.get(url_pagina, headers=capcelera, timeout=10)

        #Obtenim el temps de resposta en la descarrega de la pagina
        temps_resposta = time.time() - t0
        #Ara ja podem espaiar en el temps les succesives descarregues que poguem fer, per exemple, aplicant un delay de
        #2 vegades el temps de descarrega
        time.sleep(2 * temps_resposta)
        #o un valor fixe de 5 segons tal i com veiem en la linea seguent
        #time.sleep(5)

        # Verifiquem que la descarrega ha tingut exit
        if pagina.status_code == 200:
            print("Descarrega de la web satidfactoria (",pagina.status_code,")")

            #Inicialitzem l'objecte BeautifulSoup per al seu analisis posterior
            soup = BeautifulSoup(pagina.content, 'html.parser')
            #Localitzem l'identificador que conte les dades que necessitem recuperar (previssio setmana)
            propera_setmana = soup.find(id="seven-day-forecast")
            previsio_dies = propera_setmana.find_all(class_="tombstone-container")

            #Cerquem la previssio de tota la setmana dins del HTML descarregat
            etiq_period = propera_setmana.select(".tombstone-container .period-name")
            periodes = [pt.get_text() for pt in etiq_period]
            desc_curtes = [sd.get_text() for sd in propera_setmana.select(".tombstone-container .short-desc")]
            temperatures = [t.get_text() for t in propera_setmana.select(".tombstone-container .temp")]
            descripcions = [d["title"] for d in propera_setmana.select(".tombstone-container img")]

            #i preparem el data set amb les dades recollides
            data_set_temps = pd.DataFrame({
                    "periode": periodes,
                    "descripcio_curta": desc_curtes,
                    "temperatura": temperatures,
                    "descripcio":descripcions
                })

            #Donem un cop d'ull a com queda el data set
            print(data_set_temps)

            #Finalment copiem el data set al fitxer CSV. El fitxer l'anomenarem amb el nom del parc i la data d'extraccio
            ara = datetime.datetime.now()
            data_set_temps.to_csv('Previsio_' + nom_parc + "_" + ara.strftime("%Y-%m-%d") + '.csv', encoding='utf-8', index=False)
            print("Descarrega de les dades del parc eolic ", nom_parc, " realitzat amb exit!")

        else:
            print("Descarrega de la web erronia (", pagina.status_code, ") \n")

    #Realitzem el tractament dels errors per TimeOut o per caiguda de la pagina
    except requests.exceptions.Timeout:
        print("Atenció!!! s'ha produit un error per Timeout")
    except requests.exceptions.RequestException:
        print("Atenció!!! s'ha produit un error per caiguda de la web")


#Programa principal
#Lleguir l'XML amb les localitzacions (parcs eolics)
doc = minidom.parse("localitzacions_parcs.xml")

#obtenim les dades parc per parc del XML
parcs = doc.getElementsByTagName("parc")

#Per cada parc del fitxer fem la crida a la funcio que extreura les dades i les copiara al fitxer csv
for parc in parcs:
    #obtenim els parametres de la funcio
    nom = parc.getAttribute("name")
    gps = parc.getElementsByTagName("gps")[0]

    #Cridem a la funcio
    print("Iniciant la descarrega del parc eolic: %s " % nom, "...")
    obtenir_dades(nom, "http://forecast.weather.gov/" + gps.firstChild.data)

#Una vegada tenim tots els fitxers donem per finalitzada la extraccio
print("Fi de la extraccio de dades!!!")

##################Fi Codi########################################################################################