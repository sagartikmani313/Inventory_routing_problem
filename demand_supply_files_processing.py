import pandas as pd
import numpy as np
import time
import math
import data_processing as dp
import plant_supplier_distances as psd
from collections import defaultdict

st = time.time()

def get_demand_file(filename,sheetname):
    demand_file = pd.read_excel(filename,sheet_name=sheetname)
    demand_file = demand_file[demand_file["day"]<=28]
    conditions2 = [demand_file["day"]<=7,demand_file["day"]<=14,demand_file["day"]<=21,demand_file["day"]<=28]
    weeks = np.array([x for x in range(1,5)])
    demand_file["Week"] = np.select(conditions2, weeks)
    return demand_file

def get_supply_files(filename,sheetname):
    supply_file = pd.read_excel(filename,sheet_name=sheetname)
    supply_file.drop(supply_file.iloc[:,6:],inplace=True,axis=1)
    supply_file = supply_file[supply_file["day"]<=28]
    supply_file = supply_file[supply_file['stock init']!=0]
    conditions = [supply_file["day"]<=7,supply_file["day"]<=14,supply_file["day"]<=21,supply_file["day"]<=28]
    weeks = np.array([x for x in range(1,5)])
    supply_file["Week"] = np.select(conditions, weeks)
    return supply_file




# cluster_dict = matrix.to_dict()

    
demand_info = get_demand_file("region_3_compiled.xlsx","supplier_demand")
supply_info = get_supply_files("region_3_compiled.xlsx","plant_supply")
cluster_file = dp.get_cluster_file("region_3_compiled.xlsx","cluster_and_supplierID")
supplier_file, supplier_sublist = dp.get_supplier_file("region_3_compiled.xlsx","suppliers_and_clusterID")


#static variables
truck_capacity = 13.4 #in linear meters
loading_capacity_stable = 11 #in linear meters
loading_capacity_dynamic = 3 #in linear meters
Trucks = 6
packaging_type = len(demand_info.pack.unique()) 
total_suppliers = len(supplier_file) #56
total_clusters = len(cluster_file) #1286
Weeks = len(demand_info["Week"].unique()) #4
plants = len(supply_info["plant"].unique()) #1
supplier_list = supplier_file["index of supplier"].unique()
p2s_distance, s2s_distance, plant_dict, supplier_dict = psd.variables()
Arcs = [(i,j) for i in supplier_list for j in supplier_list if i!=j] #all possible arcs between suppliers that are not the same and not the plant.

#calling the matrix function to create the cluster-supplier matrix
matrix = dp.fill_matrix(total_suppliers,supplier_sublist,total_clusters)

#calling the function to get the distances between plants and suppliers and among suppliers.

def cluster_weekly_demand(clusters,suppliers,demand,cluster_matrix,time):
    cwd = {cluster:{week:0 for week in range(1,time+1)} for cluster in range(1,clusters+1)}
    supplier_demand_by_week = defaultdict(lambda: defaultdict(int))
    for s in range(1, suppliers + 1):
        for row in demand[(demand["supplier"] == s)].itertuples():
            supplier_demand_by_week[s][row.Week] += row.needlm

    for c in range(1, clusters + 1):
        for w in range(1, time + 1):
            for s in range(1, suppliers + 1):
                if matrix[c][s] == 1:
                    cwd[c][w] += supplier_demand_by_week[s][w]
    pd.DataFrame(cwd).T.to_excel("cluster_weekly_demand.xlsx")
    return cwd

def get_cluster_truck_capacity(cwd, capacity, number_of_trucks, number_of_clusters,weeks):
    truck_capacities = np.array([capacity*i for i in range(1, number_of_trucks + 1)])
    cluster_truck_capacity = {c:0 for c in range(1, number_of_clusters + 1)}

    for cluster in range(1,number_of_clusters + 1):
        min_error_deviation = float("inf")
        optimum_truck_capacity = None

        for truck_capacity in truck_capacities:
            sum_of_squared_differences = sum((cwd[cluster][week] - truck_capacity)**2 for week in range(1, weeks + 1))
            error_deviation = math.sqrt(sum_of_squared_differences)/weeks
            '''
            here we are calculating the error deviation for each truck capacity and then we are selecting the truck capacity 
            which has the least error deviation. The error metric that has been used is RMSE, as RMSE is a suitable metric, that balances
            both smaller and larger deviations. It's sensitive to both small and large deviations. Which helps to ensure that deviation of all
            magnitudes are penalized equally.
            '''
            if error_deviation < min_error_deviation:
                min_error_deviation = error_deviation
                optimum_truck_capacity = truck_capacity
        
        cluster_truck_capacity[cluster] = optimum_truck_capacity
    
    return cluster_truck_capacity

def stable_route_status(weekly_demand, vehicle_capacity_for_cluster,clusters,
                        truck_capacity,cluster_matrix,plant2supplier,supplier2supplier,suppliers,
                        supplier_pairs,time,minimum_truck_capacity):
    stable_route_dict = {cluster:0 for cluster in range(1,clusters+1)}

    for cluster in range(1,clusters+1):
        '''calculating the sum of distances between the plant and all the suppliers
        that are in the cluster'''

        cluster_supplier_indices = [s for s in range(1,suppliers+1) if cluster_matrix[cluster][s]==1]
        sum_of_distances = sum(plant2supplier[plant][supplier] for plant in plant2supplier for supplier in cluster_supplier_indices)
        
        '''calculating the sum of distances between all the possible supplier pairs 
        that are in the cluster and are not the same'''

        array_of_supplier_distances = [supplier2supplier[i][j] for i,j in supplier_pairs if cluster_matrix[cluster][i]==1
                                              and cluster_matrix[cluster][j]==1]
        # print(array_of_supplier_distances)
        maximum_distance = max(array_of_supplier_distances) if array_of_supplier_distances else 0
        
        for t in range(1,time+1):
            cwd = weekly_demand[cluster][t]
            best_capacity = vehicle_capacity_for_cluster[cluster]

            lower_demand_bound = math.floor(best_capacity*minimum_truck_capacity/truck_capacity)
            upper_demand_bound = math.floor((best_capacity + truck_capacity)*minimum_truck_capacity/truck_capacity)

            if cwd >= lower_demand_bound and cwd <= upper_demand_bound:
                if maximum_distance <= 200 and sum_of_distances <= 1700:
                    stable_route_dict[cluster] = 1
                else:
                    stable_route_dict[cluster] = 0
                ''''''
                break

    return stable_route_dict


weekly_demand_of_cluster = cluster_weekly_demand(total_clusters,total_suppliers,demand_info,matrix,Weeks)
cluster_truck_capacity = get_cluster_truck_capacity(weekly_demand_of_cluster,truck_capacity,Trucks,total_clusters,Weeks)
print(stable_route_status(weekly_demand_of_cluster,cluster_truck_capacity,total_clusters,truck_capacity,
                    matrix,p2s_distance,s2s_distance,total_suppliers,Arcs,Weeks,loading_capacity_stable))


et=time.time()
time_taken = round(et-st,2)
print(f"Execution time  : {time_taken} seconds")