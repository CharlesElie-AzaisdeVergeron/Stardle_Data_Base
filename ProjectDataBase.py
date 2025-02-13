"""
Ce module gère la création et le traitement d'une base de données de vaisseaux pour le jeu Star Citizen.
Il récupère les données depuis différentes sources, les nettoie et les combine dans un format utilisable.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


# Chargement et nettoyage initial de la base de données des vaisseaux
ship_db = pd.read_json("shipDB_All.json").T
# Suppression des colonnes non nécessaires
columns_to_drop = [
    'description', 'pledge_url', 'chassis_id', 'updated_at',
    'production_note', 'loaner', 'id', 'size_class', 'slug',
    'version', 'class_name', 'msrp'
]
ship_db = ship_db.drop(columns_to_drop, axis=1)

# Extraction des données de taille et de vitesse
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
        else:
            for speed_type, value in speed_data.items():
                if speed_type == 'scm':
                    scm[ship] = value
                elif speed_type == 'max':
                    max_speed[ship] = value
    return max_speed, scm


def recuperer_contenu(url, nom_classe):
    """
    Récupère le contenu HTML d'une page web selon une classe CSS.

    Args:
        url (str): URL de la page à scraper
        nom_classe (str): Nom de la classe CSS à rechercher

    Returns:
        list: Liste des éléments HTML trouvés
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
        list: Liste de textes nettoyés
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
    # Supprime les parenthèses et leur contenu
    if '(' in price_str:
        price_str = price_str[:price_str.index('(')].strip()
    return float(price_str.replace(',', ''))


# Récupération des données de prix depuis le site web
URL = 'https://scfocus.org/ship-sale-rental-locations-history/'
vaisseaux = recuperer_contenu(URL, nom_classe='column-1')
prix_html = recuperer_contenu(URL, nom_classe='column-2')

# Création du dictionnaire de prix
prix_doublons = list(zip(url_to_list(vaisseaux), url_to_list(prix_html)))
prix = dict(set(prix_doublons))

# Nettoyage des prix
input_prices = prix.copy()
del input_prices['Ship']
converted_prices = {k: clean_price(v) for k, v in input_prices.items()}

# Création de la base de données finale
stardle_db = pd.read_json('shipDB_Stardle.json').T
stardle_db = stardle_db.drop(['description', 'speed'], axis=1)

# Ajout des colonnes de vitesse et de prix
max_speeds, scm_speeds = get_speeds()
stardle_db = stardle_db.assign(
    scm=scm_speeds,
    max=max_speeds,
    price_ingame=converted_prices
)

# Sauvegarde en CSV
stardle_db.to_csv('stradle_db.csv', index=False)