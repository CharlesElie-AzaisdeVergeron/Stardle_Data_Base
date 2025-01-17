from pathlib import Path
import requests
import json

Url = "https://api.star-citizen.wiki/api/v3/vehicles?page=1&limit=1000&locale=en_EN"
script_dir = Path(__file__).parent

DataBaseType = "All" # All / Stardle / Simple

def getParameter(data:dict, key:str):
    if(key in data):
        return data[key]
    else:
        return "N/A"
    

if __name__ == "__main__":

    data = requests.get(Url)
    if data.status_code != 200:
        raise Exception("Error with reception of data")

    try:
        data = data.json()
    except:
        raise Exception("Error with json decoding")


    ShipName = {}
    ShipDB = {}

    for ship in data["data"]:
        ShipName[ship["name"]] = ship["link"]
        
        ShipData = requests.get(ship["link"])
        if(ShipData.status_code != 200 or "data" not in ShipData.json()):
            print(f"Error with reception of data for {ship['name']}")
            continue
        
        print("Data received for", ship["name"])
        ShipData = ShipData.json()["data"]
        Ship = {}

        #get only the parameters we need
        if DataBaseType == "Stardle":
            Ship["name"] = getParameter(ShipData, "name")
            Ship["manufacturer"] = getParameter(ShipData, "manufacturer")["name"]
            
            Roles = []
            role = getParameter(ShipData, "foci")
            for r in role:
                Roles.append(r["en_EN"])
            Ship["role"] = Roles
            Ship["length"] = getParameter(ShipData, "sizes")["length"]
            
            Ship["value"] = getParameter(ShipData, "skus")
            if(len(Ship["value"]) > 0):
                Ship["value"] = Ship["value"][0]["price"]
            else:
                Ship["value"] = "N/A"
            Ship["cargo"] = getParameter(ShipData, "cargo_capacity")
            Ship["crew"] = getParameter(ShipData, "crew")["max"]
            Ship["release_year"] = "" #Not Implemented

            ShipDB[ship["name"]] = Ship

        #or get a simple version of the parameters
        elif DataBaseType == "Simple":
            #Not Implemented
            pass

        #or get all the parameters
        elif DataBaseType == "All":
            ShipDB[ship["name"]] = ShipData
        
        ShipName[ship["name"]] = ship["link"]

    with open(script_dir  / "shipList.json", "w") as file:
        json.dump(ShipName, file, indent=4)
    
    with open(script_dir  / f"shipDB_{DataBaseType}.json", "w") as file:
        json.dump(ShipDB, file, indent=4)
