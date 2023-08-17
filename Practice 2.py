import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import math


def main():
    #Declaring fixed parameter values
    C=1286 #number of clusters
    S=56    #The number of suppliers
    P=1 #Number of plant
    V=[i for i in range(1,S+1)] #The list of suppliers 
    A=[(i,j) for i in V for j in V if i!=j] #The list of arcs of suppliers
    K=13.4 #The truck capacity in linear meters
    N=30    #The number of product types
    W=4 #The number of weeks
    T=6 #maximum number of trucks
    Locationfile='locationfile.xlsx'
    Demandfile='dmd_supplier_file.xlsx'
    Plantfile='supply_plant_file.xlsx'
    Clusterfile='clusterfile.txt'

    #calling functions
    demandfile=get_demandfile(demandfilecopy) #import demand file from disk
    plantfile=get_plantfile(plantfilecopy) #import plant file from disk
    locationfile=get_locationfile(locationfilecopy) #import location file from disk
    clusterfile=get_clusterfile(clusterfilecopy) #import original cluster file from disk
    cluster=create_cluster_dict(C,S) #Create cluster dictionary which take value 1 or 0 depending on whether supplier is in cluster or not
    spheric_distance=haversine_distance(lat1,lon1,lat2,lon2) #Create spheric distance dictionary
    distance=create_distance_dict(S) #Create distance dictionary with actual data
    cluster_weekly_demand=calculate_cluster_weekly_demand(demandfilecopy,Clustercopy,W,C,S)
    suitable_truck_capacity=calculate_suitable_truck_capacity(cluster_weekly_demand,W,C,K)
    stablerout_y_or_n=determine_stablerout_y_or_n(cluster_weekly_demand,suitable_truck_capacity,W,C,K,Clustercopy,Distancecopy,A)
    cluster_sumofdeviation=calculate_sumofdeviation(cluster_weekly_demand,suitable_truck_capacity,W,C)
    cluster_priority_score=calculate_cluster_priority_score(cluster_sumofdeviation,C)

def get_demandfile(Demandfile):
    demandfile=pd.read_excel(Demandfile,index_col=0)
    demandfile=demandfile[demandfile['day']<=28]
    demandfile['week']=np.where(demandfile['day']<=7,1,np.where(demandfile['day']<=14,2,np.where(demandfile['day']<=21,3,4)))
    demandfile=demandfile[demandfile['day']<=28]
    return demandfile
def get_plantfile(plantfile):
    plantfile=pd.read_excel(Plantfile,index_col=0)
    plantfile=plantfile[plantfile['day']<=28]
    plantfile['week']=np.where(plantfile['day']<=7,1,np.where(plantfile['day']<=14,2,np.where(plantfile['day']<=21,3,4)))
    return plantfile
def get_locationfile(locationfile):
    locationfile=pd.read_excel(Locationfile,index_col=0)
    return locationfile
def get_clusterfile(Clusterfile):
    infile=open(Clusterfile,'r')
    clusterfile={int(line.split(',')[0]):[int(i) for i in line.split(',')[1:]] for line in infile}
    infile.close()
    return clusterfile   
def create_cluster_dict(C,S,clusterfile):
    cluster = {i: {j: 0 for j in range(1, S+1)} for i in range(1, C+1)}   
#Checking for clusters of suppliers in the cluster file and changing the value of the Cluster dictionary to 1 if the supplier is in the cluster and 0 if not
    for i in range(1,C+1):
        for j in range(1,S+1):
            if j in clusterfile[i]:
                cluster[i][j]=1
            else:
                cluster[i][j]=0
    return cluster

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    spheric_distance = R * c
    return spheric_distance
def create_distance_dict(haversine_distance,locationfile):
    # Split the dataframe into plants and suppliers based on the 'partner_type' column
    plants_loc_file = locationfile[locationfile['partner_type'] == 'Plant']
    suppliers_loc_file= locationfile[locationfile['partner_type'] == 'Supplier']

    # Convert dataframes to dictionaries for easier access
    plants = plants_loc_file.to_dict(orient='index')
    suppliers = suppliers_loc_file.to_dict(orient='index')

    # Create the Distance dictionary
    distance_plant2suppliers = {}
    distance_supplier2supplier= {}
    # Calculate distances from each plant to every supplier
    for p, p_data in plants.items():
        distance_plant2suppliers[p] = {}
        for s, s_data in suppliers.items():
            distance_plant2suppliers[p][s] = haversine_distance(p_data['latitude'], p_data['longtitude'], s_data['latitude'], s_data['longtitude'])

        # Calculate distances from each supplier to every other supplier
    for s1, s1_data in suppliers.items():
        if s1 not in Distance:
            distance_supplier2supplier[s1] = {}
        for s2, s2_data in suppliers.items():
            if s1 != s2:
                distance_supplier2supplier[s1][s2] = haversine_distance(s1_data['latitude'], s1_data['longtitude'], s2_data['latitude'], s2_data['longtitude'])
    return distance_plant2suppliers,distance_supplier2supplier
def calculate_cluster_weekly_demand(demandfile,cluster,W,C,S):
    cluster_weekly_demand={c:{w:0 for w in range(1,W+1)} for c in range(1,C+1)} #The total demand of each cluster
    for c in range(1,C+1):
        for w in range(1,W+1):
            for s in range(1,S+1):
                if cluster[c][s]==1:
                    cluster_weekly_demand[c][w] += demandfile[(demandfile['week'] == w) & (demandfile.index == s)]['needlm'].sum()

    return cluster_weekly_demand
def calculate_suitable_truck_capacity(cluster_weekly_demand, W, C, K,T):
    list_of_truck_capacity = [K * i for i in range(1, T+1)]
    suitable_truck_capacity = {c: 0 for c in range(1, C+1)} 

    for c in range(1, C+1):
        min_deviation = float('inf')  # Initialize to a large value
        best_truck_capacity = 0

        for truck_capacity in list_of_truck_capacity:
            total_deviation = sum(abs(cluster_weekly_demand[c][w] - truck_capacity) for w in range(1, W+1))
            
            if total_deviation < min_deviation:
                min_deviation = total_deviation
                best_truck_capacity = truck_capacity

        suitable_truck_capacity[c] = best_truck_capacity

    return suitable_truck_capacity

            
def determine_stablerout_y_or_n(cluster_weekly_demand, suitable_truck_capacity, C, K, cluster, distance_plant2suppliers, distance_supplier2supplier, S, A):
    stablerout_y_or_n = {c: 0 for c in range(1, C+1)} 

    for c in range(1, C+1):
        # Calculate the sum of distances between the plant and all suppliers in the cluster once, outside the week loop
        for p, p_data in distance_plant2suppliers.items():
            distance_sum = sum(distance_plant2suppliers[p][s] for s in range(1, S+1) if cluster[c][s] == 1)
            
            # Create the list of distances for suppliers in the cluster
            supplier_distances = [distance_supplier2supplier[i][j] for i, j in A if cluster[c][i] == 1 and cluster[c][j] == 1]
            
            # Check if the list is non-empty before calling the max() function
            max_supplier_distance = max(supplier_distances) if supplier_distances else 0
            
            for w in range(1, W+1):
                if math.floor((suitable_truck_capacity[c] + K) * 0.821) > cluster_weekly_demand[c][w] >= math.floor(suitable_truck_capacity[c] * 0.821):
                    if distance_sum <= 1700 and max_supplier_distance <= 200:
                        stablerout_y_or_n[c] = 1
                    else:
                        stablerout_y_or_n[c] = 0

    return stablerout_y_or_n
def calculate_sumofdeviation(cluster_weekly_demand,suitable_truck_capacity,W,C):
    cluster_sumofdeviation={c:0 for c in range(1,C+1)} #sum of deviation of weekly demand from suitable truck capacity
    for c in range(1,C+1):
        for w in range(1,W+1):
            cluster_sumofdeviation[c]+=abs(cluster_weekly_demand[c][w]-suitable_truck_capacity[c])
    return cluster_sumofdeviation
                            
def calculate_priority_score(cluster_sumofdeviation,stable_route_y_or_n,C):
    priority_score={c:0 for c in range(1,C+1)}
    sorted_clusters = sorted(cluster_sumofdeviation.items(), key=lambda x: x[1])
    for c in range(1,C+1):
        if cluster_sumofdeviation[c]==min(cluster_sumofdeviation.values()):
            priority_score[c]=0.5+0.5*stable_route_y_or_n[c]
        else:
            for i in sorted_clusters:
                if cluster_sumofdeviation[c]==i[1]:
                    priority_score[c]=(0.5-((0.5/C)*sorted_clusters.index(i)))+0.5*stable_route_y_or_n[c]
    return priority_score
main()                      
                        
                 
