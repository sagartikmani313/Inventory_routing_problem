import gurobipy as gp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from geopy.distance import geodesic

rnd =  np.random
rnd.seed(88775)
plant_locations = pd.read_excel("region_3_compiled.xlsx",sheet_name="plant_coordinates")
supplier_locations = pd.read_excel("region_3_compiled.xlsx",sheet_name="supplier_coordinates")
supplier_locations = supplier_locations.drop("supplier id",axis=1)
plant_locations = plant_locations.drop("plant_id",axis=1)
n = len(supplier_locations)


# plant coordinates
plant_latitude = plant_locations.latitude
plant_longitude = plant_locations.longitude


# supplier coordinates on graph
plt.plot(plant_latitude,plant_longitude,c="r",marker="s",label="plant")
plt.scatter(supplier_locations["latitude"],supplier_locations["longitude"],c="b",label="supplier")

df = pd.DataFrame({"latitude":supplier_locations["latitude"],"longitude":supplier_locations["longitude"]})

def coords(l1,l2):
    return list(map(lambda x,y:(x,y),l1,l2))

supplier_coords = coords(df["latitude"],df["longitude"])
plant_coords = coords(plant_latitude,plant_longitude)

supplier_dict = {i+1:j for i,j in enumerate(supplier_coords)}
plant_dict = {i+1:j for i,j in enumerate(plant_coords)}

# function to plot the plants and suppliers of region 3 on folium map
def plot(_df):
    map_obj = folium.Map(location=[plant_latitude,plant_longitude],zoom_start=10)
    for i, r in _df.iterrows():
        lat=r["latitude"]
        lon=r["longitude"]

        if lat==plant_latitude and lon==plant_longitude:
            plant_icon = folium.Icon(color="red",icon="home",prefix="fa")
            marker=folium.Marker(location=[lat,lon],icon=plant_icon)
        else:
            supplier_icon = folium.Icon(color="blue",icon="truck",prefix="fa")
            marker=folium.Marker(location=[lat,lon],icon=supplier_icon)
        marker.add_to(map_obj)
    return map_obj.save("map.html")


def plant_to_supplier_distances(supplier,plant):
    distance = {(point,base):round(geodesic(plant.get(point),supplier.get(base)).km,2)
                               for point in plant.keys() for base in supplier.keys()}
    return distance
p2s_distance = plant_to_supplier_distances(supplier_dict,plant_dict)

def supplier_to_supplier_distances(suppliers):
    distance = {(a,b):round(geodesic(suppliers.get(a),suppliers.get(b)).km,2) for a in suppliers.keys() 
                                  for b in suppliers.keys() if a!=b}
    return distance

s2s_distance = supplier_to_supplier_distances(supplier_dict)




def variables():
    return p2s_distance,s2s_distance, plant_dict, supplier_dict

# print(variables(supplier_coords,plant_coords,distance))
#variables
# N = [i for i in range(1,n)]
# V = [0] + N
# A = [(i,j) for i in V for j in V if i!=j]
# c = {(i,j):np.hypot(df["latitude"].iloc[i]-df["latitude"].iloc[j],df["longitude"].iloc[i]-df["longitude"].iloc[j]) for i,j in A}
# Q = 20
# q = {i:df["demand"].iloc[i] for i in N}
# mdl = gp.Model("CVRP")
# x=mdl.addVars(A,vtype=gp.GRB.BINARY)
# u=mdl.addVars(N,vtype=gp.GRB.CONTINUOUS)

# # defining the model and it's objective function
# mdl.modelSense = gp.GRB.MINIMIZE
# mdl.setObjective(gp.quicksum(x[i,j]*c[i,j] for i,j in A))


# # constraints
# mdl.addConstrs(gp.quicksum(x[i, j] for j in V if j!=i)==1 for i in N)
# mdl.addConstrs(gp.quicksum(x[i, j] for i in V if i!=j)==1 for j in N)
# mdl.addConstrs((x[i,j]==1)>>(u[i]+q[j]==u[j]) for i,j in A if i!=0 and j!=0)
# mdl.addConstrs(u[i]>=q[i] for i in N)
# mdl.addConstrs(u[i]<=Q for i in N)

# mdl.Params.MIPGap = 0.1
# mdl.Params.TimeLimit = 120
# mdl.optimize()

# active_arcs = [a for a in A if x[a].x>0.99]


# for i,j in active_arcs:
#     plt.plot([df["latitude"].iloc[i],df["latitude"].iloc[j]],[df["longitude"].iloc[i],df["longitude"].iloc[j]],c="g",zorder=0)
# plt.plot(plant_latitude,plant_longitude,c="r",marker="s",label="plant")
# plt.scatter(supplier_locations["latitude"],supplier_locations["longitude"],c="b",label="supplier")
# plt.show()

# def plot_op(_df):
#     map_obj = folium.Map(location=[plant_latitude,plant_longitude],zoom_start=10)
#     for i, r in _df.iterrows():
#         lat=r["latitude"]
#         lon=r["longitude"]

#         if lat==plant_latitude and lon==plant_longitude:
#             plant_icon = folium.Icon(color="red",icon="home",prefix="fa")
#             marker=folium.Marker(location=[lat,lon],icon=plant_icon)
#         else:
#             supplier_icon = folium.Icon(color="blue",icon="truck",prefix="fa")
#             marker=folium.Marker(location=[lat,lon],icon=supplier_icon)
#         marker.add_to(map_obj)

#     for i, j in active_arcs:
#         arc_coords = [(_df["latitude"].iloc[i], _df["longitude"].iloc[i]),
#                       (_df["latitude"].iloc[j], _df["longitude"].iloc[j])]
#         polyline = folium.PolyLine(locations=arc_coords, color="green")
#         polyline.add_to(map_obj)
#     map_obj.save("Op_map.html")

# plot_op(df)