import gurobipy as gp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic

rnd =  np.random
rnd.seed(88775)
def get_plant_locationFile(filename,sheetname):

    '''This function returns the plant location file in the form of a dataframe'''

    plant_file = pd.read_excel(filename,sheet_name=sheetname)
    plant_file = plant_file.drop("plant id",axis=1)
    print("Plant file processed")
    return plant_file
def get_supplier_locationFile(filename,sheetname):

    '''This function returns the supplier location file in the form of a dataframe'''

    supplier_file = pd.read_excel(filename,sheet_name=sheetname)
    supplier_file = supplier_file.drop("supplier id",axis=1)
    print("Supplier file processed")
    return supplier_file

plant_locations = get_plant_locationFile("region_3_compiled.xlsx","plant_coordinates")
supplier_locations = get_supplier_locationFile("region_3_compiled.xlsx","supplier_coordinates") 
n = len(supplier_locations)


# plant coordinates
# plant_latitude = plant_locations.latitude
# plant_longitude = plant_locations.longitude


# supplier coordinates on graph
# plt.plot(plant_latitude,plant_longitude,c="r",marker="s",label="plant")
# plt.scatter(supplier_locations["latitude"],supplier_locations["longitude"],c="b",label="supplier")

df = pd.DataFrame({"latitude":supplier_locations["latitude"],"longitude":supplier_locations["longitude"]})
df2 = pd.DataFrame({"latitude":plant_locations["latitude"],"longitude":plant_locations["longitude"]})

def coords(l1,l2):

    '''This function returns the coordinates of the suppliers and plants in the form of a list'''

    return list(map(lambda x,y:(x,y),l1,l2))

def get_locations(data,data2):

    '''This function returns the coordinates of the suppliers and plants in the form of a dictionary using the coords() function'''

    supplier_coords = coords(data["latitude"],data["longitude"])
    plant_coords = coords(data2["latitude"],data2["longitude"])
    supply = {i+1:j for i,j in enumerate(supplier_coords)}
    plant = {i+1:j for i,j in enumerate(plant_coords)}
    print("Locations processed")
    return supply,plant
supplier_dict,plant_dict = get_locations(df,df2)

def plant_to_supplier_distances(supplier,plant):

    '''This function returns the distance between the plants and suppliers in the form of a dictionary'''

    distance = {point:{base:round(geodesic(plant.get(point),supplier.get(base)).km,2) for base in supplier.keys()} for point in plant.keys()}
    print("Plant to supplier Distances processed")
    return distance
p2s_distance = plant_to_supplier_distances(supplier_dict,plant_dict)

def supplier_to_supplier_distances(suppliers):

    '''This function returns the distance between the suppliers in the form of a dictionary'''

    distance = {a:{b:round(geodesic(suppliers.get(a),suppliers.get(b)).km,2) for b in suppliers.keys() if a!=b} for a in suppliers.keys()}
    print("Supplier to supplier Distances processed")
    return distance

s2s_distance = supplier_to_supplier_distances(supplier_dict)


def variables():

    '''This function returns the variables to be used in the heuristic in a different file'''

    print("Variables processed")
    return p2s_distance,s2s_distance, plant_dict, supplier_dict