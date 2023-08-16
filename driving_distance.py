import requests
import plant_supplier_distances as psd
import pandas as pd
import numpy as np

p2s,s2s,plant_dict,supplier_dict = psd.variables()

def get_driving_distance(api_key, origin, destination):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if "rows" in data and data["rows"][0]["elements"][0]["status"] == "OK":
        distance = data["rows"][0]["elements"][0]["distance"]["text"]
        return distance
    else:
        return None


def driving_distance(plant,supplier,api_key):
    distances = {}
    for plant_coord in plant.values():
        for supplier_id, supplier_coord in supplier.items():
            origin = f"{plant_coord[0]},{plant_coord[1]}"
            destination = f"{supplier_coord[0]},{supplier_coord[1]}"
            distance = get_driving_distance(api_key,origin,destination)
            distances[supplier_id] = distance
        
    return distances

api_key = "AIzaSyCNmwldeQZnF15l1mVE67DKz7nnmT8NLHY"
a = driving_distance(plant_dict,supplier_dict,api_key)
print(a)