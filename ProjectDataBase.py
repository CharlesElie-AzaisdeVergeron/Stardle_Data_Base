"""
Ce module gère la création et le traitement d'une base de données de vaisseaux pour le jeu Star Citizen.
Il récupère les données depuis différentes sources, les nettoie et les combine dans un format utilisable.

Classes: Aucune
Functions:
    - get_speeds: Extrait les données de vitesse des vaisseaux
    - sizes: Extrait les dimensions des vaisseaux
    - recuperer_contenu: Récupère le contenu HTML d'une page web
    - url_to_list: Convertit les éléments HTML en liste
    - clean_price: Nettoie et convertit les prix
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np

# Constantes globales
URL_SHIP_PRICES = 'https://scfocus.org/ship-sale-rental-locations-history/'
COLUMNS_TO_DROP = [
    'description', 'pledge_url', 'chassis_id', 'updated_at',
    'production_note', 'loaner', 'id', 'size_class', 'slug',
    'version', 'class_name', 'msrp'
]

# Chargement et nettoyage initial de la base de données des vaisseaux
ship_db = pd.read_json("/home/leferre/Bureau/Fac/base de données/Projet/Stardle_Data_Base/shipDB_All.json").T
ship_db = ship_db.drop(COLUMNS_TO_DROP, axis=1)

# Extraction des données de base
SIZES = dict(ship_db['sizes'])
SPEED = dict(ship_db['speed'])


def get_speeds(speed_dict=SPEED):
    """
    Extrait les vitesses SCM et maximales des vaisseaux.

    Args:
        speed_dict (dict): Dictionnaire contenant les données de vitesse

    Returns:
        tuple: Deux dictionnaires (vitesses maximales, vitesses SCM)
    """
    scm = {}
    max_speed = {}
    
    for ship, speed_data in speed_dict.items():
        if str(speed_data) == 'None':
            scm[ship] = max_speed[ship] = 'None'
            continue
        
        for speed_type, value in speed_data.items():
            if speed_type == 'scm':
                scm[ship] = value
            elif speed_type == 'max':
                max_speed[ship] = value
                
    return max_speed, scm


def sizes(dimensions_dict=SIZES):
    """
    Extrait les dimensions des vaisseaux.

    Args:
        dimensions_dict (dict): Dictionnaire contenant les données de dimensions

    Returns:
        tuple: Trois dictionnaires (length, beam, height)
    """
    length = {}
    beam = {}
    height = {}

    for ship, dimensions in dimensions_dict.items():
        for dim_type, value in dimensions.items():
            if dim_type == 'length':
                length[ship] = value
            elif dim_type == 'beam':
                beam[ship] = value
            else:
                height[ship] = value
    
    return length, beam, height


def recuperer_contenu(url, nom_classe):
    """
    Récupère le contenu HTML d'une page web selon une classe CSS.

    Args:
        url (str): URL de la page à scraper
        nom_classe (str): Nom de la classe CSS à rechercher

    Returns:
        list: Liste des éléments HTML trouvés

    Raises:
        requests.RequestException: En cas d'erreur lors de la requête HTTP
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find_all(class_=nom_classe)


def url_to_list(html_elements):
    """
    Convertit les éléments HTML en liste de texte nettoyé.

    Args:
        html_elements (list): Liste d'éléments HTML

    Returns:
        list: Liste de textes nettoyés, sans le premier élément
    """
    cleaned_list = []
    for element in html_elements:
        text = element.text.replace("\n", "|").replace("\t", "")
        cleaned_list.extend(text.split("|"))
    return cleaned_list[1:]


def clean_price(price_str):
    """
    Nettoie et convertit une chaîne de prix en nombre flottant.

    Args:
        price_str (str): Prix sous forme de chaîne

    Returns:
        float: Prix converti en nombre
    """
    if '(' in price_str:
        price_str = price_str[:price_str.index('(')].strip()
    return float(price_str.replace(',', ''))


def main():
    """Fonction principale exécutant la logique du programme."""
    # Récupération des données de prix
    vaisseaux = recuperer_contenu(URL_SHIP_PRICES, nom_classe='column-1')
    prix_html = recuperer_contenu(URL_SHIP_PRICES, nom_classe='column-2')

    # Traitement des prix
    prix_doublons = list(zip(url_to_list(vaisseaux), url_to_list(prix_html)))
    prix = dict(set(prix_doublons))
    input_prices = prix.copy()
    del input_prices['Ship']
    converted_prices = {k: clean_price(v) for k, v in input_prices.items()}

    # Création de la base de données finale
    stardle_db = pd.read_json('/home/leferre/Bureau/Fac/base de données/Projet/Stardle_Data_Base/shipDB_Stardle.json').T
    stardle_db = stardle_db.drop(['description', 'speed'], axis=1)

    # Ajout des colonnes calculées
    max_speeds, scm_speeds = get_speeds()
    length_dict, beam_dict, height_dict = sizes()

    # Mise à jour du DataFrame
    stardle_db = stardle_db.assign(
        scm=scm_speeds,
        max=max_speeds,
        price_ingame=converted_prices,
        length=length_dict,
        beam=beam_dict,
        height=height_dict
    )

    stardle_db= stardle_db.replace({None: np.nan})
    stardle_db['mass'] = stardle_db['mass'].astype(np.float64)
    
    colonnes_numeriques = stardle_db.select_dtypes(include=['int64', 'float64'])

    for i in colonnes_numeriques.keys():
        stardle_db[i].replace(np.nan,stardle_db[i].mean(), inplace=True)
    
    stardle_db.drop('dimensions', axis=1, inplace=True)
    
    # Sauvegarde en CSV
    stardle_db.to_csv('stradle_db.csv', index=False)

if __name__ == "__main__":
    main()