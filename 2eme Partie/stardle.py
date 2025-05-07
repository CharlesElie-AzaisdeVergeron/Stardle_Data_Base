import random
import pandas as pd
import numpy as np


data = pd.read_csv('donnees.csv')

colonnes = list(data.columns)
colonnes_qualitatives=[]
colonnes_quantitatives=[]
for col in colonnes : 
    try:
        pd.to_numeric(data[col])
        #colonnes_quantitatives.append(str(col))
    except :
        colonnes_qualitatives.append(col)
        print(col, 'est une variable qualitative')
for col in colonnes :
    if col not in colonnes_qualitatives:
        colonnes_quantitatives.append(col)



def choisir_mot():
    return random.choice(list(data['name']))
def aide_a_trouver_nom_vaisseau(nom_partiel):
    res=[]
    for nom in list(data.index):
        if len(nom_partiel)<=len(nom):
            compatible=True
            for k in range(len(nom_partiel)):
                if nom_partiel[k]!=nom[k]:
                    compatible=False
            if compatible : 
                res.append(nom)
    return res

def verifier_ship(ship_secret, ship_guess):
    
    # Vérifie si la tentative existe dans le DataFrame
    if not ship_guess in list(data['name']):
        return "Ce vaisseau n'existe pas dans la base de données!"

    # Indique quand c'est la bonne réponse
    if ship_guess==ship_secret :
        return 'Bravo, vous avez trouvez le bon vaisseau!'

    L=list(data['name'])
    k = L.index(ship_guess)
    a = L.index(ship_secret)
    res='Vous vous êtes trompés de vaisseau. Voici les résultats de chaque variables :'
    for col in data.columns : 
        if not col in ['Unnamed: 0','name']:
            res+='\n '
            res+='-pour la variable '
            res+=col
            res+=' '
            if col in colonnes_qualitatives :
                if data[col][k]!=data[col][a]:
                    res+='ce n est pas la bonne réponse'
                else:
                    res+='c est la bonne réponse✅'
            if col in colonnes_quantitatives : 
                if 0.9*data[col][a]<=data[col][k]<=1.1*data[col][a]:
                    res+=' c est peut etre la bonne réponse🟡'
                else:
                    res+='ce n est pas la bonne réponse❌'

    print(res)
    return 0   

def stardle():
    ship_secret = choisir_mot()
    tentatives = 6
    print("Bienvenue dans Stardle! Devine le vaisseau")
    
    print("Liste des vaisseaux disponibles:")
    for idx, name in enumerate(data['name']):
        print(f"{idx + 1}. {name}")
    
    for _ in range(tentatives):
        
        tentative = input("Entrez votre tentative: ")
            
        # Vérifie si le mot existe
        resultat = verifier_ship(ship_secret,ship_guess=tentative)
        if resultat == "Ce vaisseau n'existe pas dans la base de données!":
            print(resultat)
            continue
            
        print(resultat)
        
        #if all(car == "✅" for car in resultat if car in ["✅", "🟡", "❌"]):
        if resultat!=0:
            print("Félicitations! Vous avez trouvé le vaisseau!")
            break
    else:
        print(f"Désolé, vous avez épuisé vos tentatives. Le vaisseau était: {ship_secret}")
        

stardle()       