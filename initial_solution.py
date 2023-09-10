import demand_supply_files_processing as dsfp
import pandas as pd
import numpy as np
import time

st = time.time()

cluster_importance = dsfp.cluster_importance
weekly_cluster_demand = dsfp.weekly_demand_of_cluster
cluster_truck_capacity = dsfp.cluster_truck_capacity
stable_route_info = dsfp.stable_route_info
demand_info = dsfp.demand_info
supply_info = dsfp.supply_info
truck_capacity = dsfp.truck_capacity
loading_capacity_stable  = dsfp.loading_capacity_stable
loading_capacity_dynamic = dsfp.loading_capacity_dynamic
trucks = dsfp.Trucks
packaging_type = dsfp.packaging_type
total_suppliers = dsfp.total_suppliers
total_clusters = dsfp.total_clusters
weeks = dsfp.Weeks
plants = dsfp.plants
suppliers = dsfp.supplier_list
arcs =  dsfp.Arcs
matrix = dsfp.matrix

def route_scores(stable_route_status,cluster_priority):
    dynamic_route_clusters = np.array([a for a in stable_route_status.keys() if stable_route_status[a] == 0])
    stable_route_clusters = np.array([a for a in stable_route_status.keys() if stable_route_status[a] != 0])
    stable_route_importance_scores = {a:b for a,b in cluster_priority.items() if a in stable_route_clusters}
    stable_route_importance_scores = dict(sorted(stable_route_importance_scores.items(), key=lambda item: item[1],reverse=True))
    dynamic_route_importance_scores = {a:b for a,b in cluster_priority.items() for a in dynamic_route_clusters}
    dynamic_route_importance_scores = dict(sorted(dynamic_route_importance_scores.items(), key=lambda item: item[1],reverse=True))
    print("Importance scores calculated")
    return stable_route_importance_scores,dynamic_route_importance_scores

def genarate_weekly_cluster_info(weekly_demand,cluster_priority,cluster_capacity,clusters,route_status,time_frame):
    weekly_demand_file = pd.DataFrame(weekly_demand.values())
    cluster_data = pd.DataFrame({"cluster_id":range(1,clusters+1),
                                "priority":cluster_priority.values(),
                                "Week_1_demand_inLM":weekly_demand_file.iloc[:,0],
                                "Week_2_demand_inLM":weekly_demand_file.iloc[:,1],
                                "Week_3_demand_inLM":weekly_demand_file.iloc[:,2],
                                "Week_4_demand_inLM":weekly_demand_file.iloc[:,3],
                                "stable_route_status":route_status.values()})
    # sorted_cluster_data = cluster_data.sort_values(by=["priority"],ascending=False,ignore_index=True)
    cluster_data["best_truck_capacity"] = cluster_capacity.values()
    time = range(1,time_frame+1)
    for week in time:
        shortage_col = f"W{week}_shortage"
        week_demand_col = f"Week_{week}_demand_inLM"
        
        cluster_data[shortage_col] = np.where(cluster_data[week_demand_col] > cluster_data["best_truck_capacity"],
                                            abs(cluster_data["best_truck_capacity"]-cluster_data[week_demand_col]),0)
    cluster_data["Total_shortage"] = cluster_data["W1_shortage"]+cluster_data["W2_shortage"]+cluster_data["W3_shortage"]+cluster_data["W4_shortage"]

    mask = cluster_data["stable_route_status"]==1
    cluster_data.loc[mask,"stable_routes"] = cluster_data["best_truck_capacity"] / truck_capacity
    cluster_data.loc[mask,"dynamic_routes"] = 0
    cluster_data.loc[~mask,"stable_routes"] = 0
    cluster_data.loc[~mask,"dynamic_routes"] = cluster_data["best_truck_capacity"] / truck_capacity

    cluster_data["dynamic_routes"] = cluster_data["dynamic_routes"].astype(int)
    cluster_data["stable_routes"] = cluster_data["stable_routes"].astype(int)
    cluster_data = cluster_data.sort_values(by=["priority"],ascending=False,ignore_index=True)
    print("Weekly cluster data generated")
    return cluster_data

stable_route_importance,dynamic_route_importance = route_scores(stable_route_info,cluster_importance)
cluster_weekly_data = genarate_weekly_cluster_info(weekly_cluster_demand,cluster_importance,cluster_truck_capacity,
                                                   total_clusters,stable_route_info,weeks)



et=time.time()
time_taken = round(et-st,2)
print(f"Execution time: {time_taken} seconds")

