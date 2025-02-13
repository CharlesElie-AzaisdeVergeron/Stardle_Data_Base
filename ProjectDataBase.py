import pandas as pd
import requests
from bs4 import BeautifulSoup
import re



ship_db = pd.read_json("shipDB_All.json").T
ship_db = ship_db.drop(['description','pledge_url','chassis_id','updated_at','production_note','loaner','id','size_class','slug','version','class_name','msrp'], axis = 1)
Sizes = dict(ship_db['sizes'])
Speed = dict(ship_db['speed'])

def Speeds(D=Speed):
    scm={}
    maxi = {}
    
    for k,v in Speed.items():
        if str(v) == 'None':
            scm[k]=maxi[k]='None'
        else : 
            for i,j in v.items():
                if i == 'scm':
                    scm[k]= j
                elif i == 'max':
                    maxi[k] = j  
    return maxi,scm

def recuperer_contenu(url, nom_classe):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    balises = soup.find_all(class_=nom_classe)
    
    return balises

vaisseaux =  recuperer_contenu('https://scfocus.org/ship-sale-rental-locations-history/',nom_classe= 'column-1')
prix= recuperer_contenu('https://scfocus.org/ship-sale-rental-locations-history/',nom_classe= 'column-2')

def url_to_list(D):
    L =[]
    for e in D:
        e = e.text.replace("\n", "|").replace("\t", "")
        e = e.split("|")
        L += e
    return L[1:]

prix_doublons= [i for i in zip(url_to_list(vaisseaux),url_to_list(prix))]
prix = dict(set(prix_doublons))


input_prices = prix
#del  input_prices['Ship']

def clean_price(price_str):
    # Remove any parentheses and their content
    if '(' in price_str:
        price_str = price_str[:price_str.index('(')].strip()
    return float(price_str.replace(',', ''))
    # Remove commas and convert to float
    #return float(price_str.replace(',', ''))
    
converted_prices = {k: clean_price(v) for k, v in input_prices.items()}

stardle_db = pd.read_json('shipDB_Stardle.json').T
stardle_db = stardle_db.drop('description',axis = 1)
stardle_db = stardle_db.drop(['speed'],axis=1)

stardle_db = stardle_db.assign(scm = Speeds()[1],
                         max = Speeds()[0])

stardle_db = stardle_db.assign(price_ingame = converted_prices)

stardle_db.to_csv('stradle_db.csv', index=False)