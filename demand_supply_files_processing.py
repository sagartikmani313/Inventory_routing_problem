import pandas as pd
import numpy as np
import time
import math

'''self made modules'''
import data_processing as dp 
import plant_supplier_distances as psd

from collections import defaultdict

st = time.time()

def get_demand_file(filename,sheetname):

    '''This function takes the demand file as input and 
    returns the demand file with the week column added to it.'''

    demand_file = pd.read_excel(filename,sheet_name=sheetname)
    demand_file = demand_file[demand_file["day"]<=28]
    conditions2 = [demand_file["day"]<=7,demand_file["day"]<=14,demand_file["day"]<=21,demand_file["day"]<=28]
    weeks = np.array([x for x in range(1,5)])
    demand_file["Week"] = np.select(conditions2, weeks)
    print("Demand file processed")
    return demand_file

def get_supply_files(filename,sheetname):

    '''This function takes the supply file as input and returns the 
    supply file with the week column added to it.'''

    supply_file = pd.read_excel(filename,sheet_name=sheetname)
    supply_file.drop(supply_file.iloc[:,6:],inplace=True,axis=1)
    supply_file = supply_file[supply_file["day"]<=28]
    supply_file = supply_file[supply_file['stock init']!=0]
    conditions = [supply_file["day"]<=7,supply_file["day"]<=14,supply_file["day"]<=21,supply_file["day"]<=28]
    weeks = np.array([x for x in range(1,5)])
    supply_file["Week"] = np.select(conditions, weeks)
    print("Supply file processed")
    return supply_file

'''getting the demand and supply file'''
demand_info = get_demand_file("region_3_compiled.xlsx","supplier_demand")
supply_info = get_supply_files("region_3_compiled.xlsx","plant_supply")

'''getting the cluster and supplier file from different module'''
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

#all possible arcs between suppliers that are not the same and not the plant.
Arcs = [(i,j) for i in supplier_list for j in supplier_list if i!=j] 

#calling the matrix function to create the cluster-supplier matrix
'''user defined functions are called here from different modules'''
matrix = dp.fill_matrix(total_suppliers,supplier_sublist,total_clusters)
# cluster_dict = matrix.to_dict()

#calling the function to get the distances between plants and suppliers and among suppliers.

def cluster_weekly_demand(clusters,suppliers,demand,cluster_matrix,time):

    '''This function takes the number of clusters, number of suppliers, demand file, cluster-supplier matrix and the number of weeks as input
    and returns the cluster weekly demand as output in the form of a dictionary.'''

    cwd = {cluster:{week:0 for week in range(1,time+1)} for cluster in range(1,clusters+1)}
    supplier_demand_by_week = defaultdict(lambda: defaultdict(int))
    for s in range(1, suppliers + 1):
        for row in demand[(demand["supplier"] == s)].itertuples():
            supplier_demand_by_week[s][row.Week] += row.needlm

    for c in range(1, clusters + 1):
        for w in range(1, time + 1):
            for s in range(1, suppliers + 1):
                if cluster_matrix[c][s] == 1:
                    cwd[c][w] += supplier_demand_by_week[s][w]
    # pd.DataFrame(cwd).T.to_excel("cluster_weekly_demand.xlsx")
    print("Cluster weekly demand calculated")
    return cwd

def get_cluster_truck_capacity(cwd, capacity, number_of_trucks, number_of_clusters,weeks):

    '''This function takes the cluster weekly demand, truck capacity, number of trucks, number of clusters and number of weeks as input
    and returns the cluster truck capacity as output in the form of a dictionary.'''

    truck_capacities = np.array([capacity*i for i in range(1, number_of_trucks + 1)])
    cluster_truck_capacity = {c:0 for c in range(1, number_of_clusters + 1)}

    for cluster in range(1,number_of_clusters + 1):
        min_error_deviation = float("inf")
        optimum_truck_capacity = None

        for truck_capacity in truck_capacities:
            # error_deviation = sum(abs(cwd[cluster][week] - truck_capacity) for week in range(1, weeks + 1))
            '''here RMSE and Sum of absolute errors both were used to calculate the error deviation. Both had the same answer but 
            RMSE was selected as the error metric, as RMSE is a suitable metric, that balances both smaller and larger deviations.'''
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

    # Saving the cluster truck capacity in an excel file 
    # cluster_truck_capacity_df = pd.DataFrame(cluster_truck_capacity.items(),index=cluster_truck_capacity.keys(),columns=["Cluster","Truck Capacity"])
    # cluster_truck_capacity_df.to_excel("cluster_truck_capacity.xlsx")

    print("Cluster truck capacity calculated")
    return cluster_truck_capacity

def stable_route_status(weekly_demand, vehicle_capacity_for_cluster,clusters,
                        truck_capacity,cluster_matrix,plant2supplier,supplier2supplier,suppliers,
                        supplier_pairs,time,minimum_truck_capacity):
    
    '''This function takes the cluster weekly demand, cluster truck capacity, number of clusters, truck capacity, cluster-supplier matrix,
    plant to supplier distance, supplier to supplier distance, number of suppliers, supplier pairs, number of weeks and minimum truck capacity
    as input and returns the stable route status as output in the form of a dictionary.'''
    
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
        
        maximum_distance = max(array_of_supplier_distances) if array_of_supplier_distances else 0
        
        for t in range(1,time+1):
            cwd = weekly_demand[cluster][t]
            best_capacity = vehicle_capacity_for_cluster[cluster]

            '''here minimum truck capacity is the loading requirement of the truck, which is 11 linear meters.
            for stable routes. This variable represents a factor that defines the minimum proportion of a truck's capacity that should be 
            used for transportation. For example, if minimum_truck_capacity is 0.8, it means that at least 80% of a 
            truck's capacity should be utilized to be considered efficient.'''

            lower_demand_bound = math.floor(best_capacity*minimum_truck_capacity/truck_capacity)
            upper_demand_bound = math.floor((best_capacity + truck_capacity)*minimum_truck_capacity/truck_capacity)

            '''the above calculations ensure that the demand for transportation in a cluster is neither too low (below the minimum truck capacity
            utilisation) nor too high (exceeding the combined capacity of two trucks) Its a way of optimising the truck usage to balance demand
            and capacity, considering the constraints set by minimum truck capacity and maximum truck capacity.'''

            if cwd >= lower_demand_bound and cwd <= upper_demand_bound:
                if maximum_distance <= 200 and sum_of_distances <= 1700:
                    stable_route_dict[cluster] = 1
                else:
                    stable_route_dict[cluster] = 0
    
    # Saving the stable route status in an excel file
    # stable_route_df = pd.DataFrame(stable_route_dict.items(),index=stable_route_dict.keys(),columns=["Cluster","Stable Route"])
    # stable_route_df.to_excel("stable_route_status.xlsx")

    print("Stable route status generated")
    return stable_route_dict



def get_sum_of_error_deviations(weekly_demand, vehicle_capacity_for_cluster,clusters, time):

    '''This function takes the cluster weekly demand, cluster truck capacity, number of clusters and number of weeks as input and returns
    the sum of error deviations as output in the form of a dictionary.'''
    
    sum_of_error_deviations = {c:0 for c in range(1,clusters+1)}
    # for c in range(1,clusters+1):
    #     for t in range(1,time+1):
    #         sum_of_error_deviations[c] += (abs(weekly_demand[c][t] - vehicle_capacity_for_cluster[c]))
    # print(sum_of_error_deviations)
    for c in range(1,clusters+1):
        demand = weekly_demand[c]
        capacity = vehicle_capacity_for_cluster[c]
        error_deviations = [(demand[t] - capacity)**2 for t in range(1,time+1)]
        mean_error_deviation = sum(error_deviations)/time
        rmse = math.sqrt(mean_error_deviation)
        sum_of_error_deviations[c] = rmse
    return sum_of_error_deviations

# print("Sum of error deviations calculated")


def generating_priority_metric(errors_of_cluster,stable_route_status,clusters):

    '''This function takes the sum of error deviations, stable route status and number of clusters as input and returns the priority metric
    as output in the form of a dictionary.
    The priority metric is calculated as follows:   
    1. The cluster with the minimum error deviation is given a priority of 0.5
    2. The cluster with the maximum error deviation is given a priority of 1
    3. The clusters in between are given a priority of 0.5 - ((0.5/clusters)*index of the cluster in the sorted list of 
    clusters by error deviation.
    4. The priority metric is then multiplied by the stable route status of the cluster.
    '''

    priority_metric = {c:0 for c in range(1,clusters+1)}
    sorted_clusters_by_errors = sorted(errors_of_cluster.items(),key=lambda x:x[1])
    min_error = min(errors_of_cluster.values())

    for c in range(1,clusters+1):
        if errors_of_cluster[c] == min_error:
            priority_metric[c] = 0.5+0.5*stable_route_status[c]
        else:
            sorted_index = next(i for i, (_,error) in enumerate(sorted_clusters_by_errors) if error == errors_of_cluster[c])
            priority_metric[c] = (0.5 - ((0.5/clusters)*sorted_index)) + 0.5*stable_route_status[c]
    sorted_priority_metric = sorted(priority_metric.items(),key=lambda x:x[1],reverse=True)
    # pd.DataFrame(sorted_priority_metric).to_excel("priority_metric.xlsx")
    print("Priority metrics generated")
    return sorted_priority_metric




weekly_demand_of_cluster = cluster_weekly_demand(total_clusters,total_suppliers,demand_info,matrix,Weeks)
cluster_truck_capacity = get_cluster_truck_capacity(weekly_demand_of_cluster,truck_capacity,Trucks,total_clusters,Weeks)
stable_route_info = stable_route_status(weekly_demand_of_cluster,cluster_truck_capacity,total_clusters,truck_capacity,
                    matrix,p2s_distance,s2s_distance,total_suppliers,Arcs,Weeks,loading_capacity_stable)
cluster_error_total = get_sum_of_error_deviations(weekly_demand_of_cluster,cluster_truck_capacity,total_clusters,Weeks)
cluster_importance = generating_priority_metric(cluster_error_total,stable_route_info,total_clusters)
print("All files processed")


et=time.time()
time_taken = round(et-st,2)
print(f"Execution time: {time_taken} seconds")