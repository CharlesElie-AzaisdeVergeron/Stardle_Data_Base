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
COLUMNS_TO_DROP = [
    'description', 'pledge_url', 'chassis_id', 'updated_at',
    'production_note', 'loaner', 'id', 'size_class', 'slug',
    'version', 'class_name', 'msrp'
]

# Chargement et nettoyage initial de la base de données des vaisseaux
bd_vaisseaux = pd.read_json(
    "/home/leferre/Bureau/Fac/base de données/Projet/Stardle_Data_Base/shipDB_All.json"
).T
bd_vaisseaux = bd_vaisseaux.drop(COLUMNS_TO_DROP, axis=1)

# Extraction des données de base
DIMENSIONS = dict(bd_vaisseaux['sizes'])
VITESSES = dict(bd_vaisseaux['speed'])


def obtenir_vitesses(dict_vitesses=VITESSES):
    """
    Extrait les vitesses SCM et maximales des vaisseaux.

    Args:
        dict_vitesses (dict): Dictionnaire contenant les données de vitesse

    Returns:
        tuple: Deux dictionnaires (vitesses maximales, vitesses SCM)
    """
    scm = {}
    vitesse_max = {}

    for vaisseau, donnees_vitesse in dict_vitesses.items():
        if str(donnees_vitesse) == 'None':
            scm[vaisseau] = vitesse_max[vaisseau] = 'None'
            continue
        
        for type_vitesse, valeur in donnees_vitesse.items():
            if type_vitesse == 'scm':
                scm[vaisseau] = valeur
            elif type_vitesse == 'max':
                vitesse_max[vaisseau] = valeur
                
    return vitesse_max, scm


def dimensions(dict_dimensions=DIMENSIONS):
    """
    Extrait les dimensions des vaisseaux.

    Args:
        dict_dimensions (dict): Dictionnaire contenant les données de dimensions

    Returns:
        tuple: Trois dictionnaires (longueur, largeur, hauteur)
    """
    longueur = {}
    largeur = {}
    hauteur = {}

    for vaisseau, dims in dict_dimensions.items():
        for type_dim, valeur in dims.items():
            if type_dim == 'length':
                longueur[vaisseau] = valeur
            elif type_dim == 'beam':
                largeur[vaisseau] = valeur
            else:
                hauteur[vaisseau] = valeur

    return longueur, largeur, hauteur


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


def html_vers_liste(elements_html):
    """
    Convertit les éléments HTML en liste de texte nettoyé.

    Args:
        elements_html (list): Liste d'éléments HTML

    Returns:
        list: Liste de textes nettoyés, sans le premier élément
    """
    liste_nettoyee = []
    for element in elements_html:
        texte = element.text.replace("\n", "|").replace("\t", "")
        liste_nettoyee.extend(texte.split("|"))
    return liste_nettoyee[1:]


def nettoyer_prix(chaine_prix):
    """
    Nettoie et convertit une chaîne de prix en nombre flottant.

    Args:
        chaine_prix (str): Prix sous forme de chaîne

    Returns:
        float: Prix converti en nombre
    """
    if '(' in chaine_prix:
        chaine_prix = chaine_prix[:chaine_prix.index('(')].strip()
    return float(chaine_prix.replace(',', ''))


def main():

    # Création de la base de données finale
    bd_stardle = pd.read_json(
        '/home/leferre/Bureau/Fac/base de données/Projet/Stardle_Data_Base/shipDB_Stardle.json'
    ).T
    bd_stardle = bd_stardle.drop(['description', 'speed', 'dimensions'], axis=1)

    # Ajout des colonnes calculées
    vitesses_max, vitesses_scm = obtenir_vitesses()
    dict_longueur, dict_largeur, dict_hauteur = dimensions()
    donnees_jeu = pd.read_csv(
        '/home/leferre/Bureau/Fac/base de données/Projet/Stardle_Data_Base/#DPSCalculatorCART(1).csv'
    )
    donnees_jeu.drop(
        ['Shop', 'Location', 'System', 'Quantity', 'Unnamed: 6'],
        axis=1,
        inplace=True
    )
    dict_jeu = pd.DataFrame.to_dict(donnees_jeu)
    valeurs = list(dict_jeu.values())
    noms = list(valeurs[0].values())
    prix = list(valeurs[1].values())
    dict_prix = {}

    for nom, prix in zip(noms, prix):
        dict_prix[nom] = prix
        
    # Mise à jour du DataFrame
    bd_stardle = bd_stardle.assign(
        prix_jeu=dict_prix,
        scm=vitesses_scm,
        max=vitesses_max,
        longueur=dict_longueur,
        largeur=dict_largeur,
        hauteur=dict_hauteur
    )
    
    # Sauvegarde en CSV
    bd_stardle.to_csv('bd_stardle.csv', index=False)

if __name__ == "__main__":
    main()