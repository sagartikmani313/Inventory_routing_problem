import pandas as pd
import numpy as np
import time
import data_processing as dp
# import plant_supplier_distances as psd

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

demand_info = get_demand_file("region_3_compiled.xlsx","supplier_demand")
supply_info = get_supply_files("region_3_compiled.xlsx","plant_supply")
cluster_file = dp.get_cluster_file("region_3_compiled.xlsx","cluster_and_supplierID")
supplier_file, supplier_sublist = dp.get_supplier_file("region_3_compiled.xlsx","suppliers_and_clusterID")


#static variables
truck_capacity = 13.4 #in linear meters
loading_capacity_stable = 11 #in linear meters
loading_capacity_dynamic = 3 #in linear meters
total_clusters = len(cluster_file)
total_suppliers = len(supplier_file)
Weeks = len(demand_info["Week"].unique())
plants = len(supply_info["plant"].unique())
suppliers = len(supplier_file["supplier id"].unique())
supplier_list = supplier_file["index of supplier"].unique()


et=time.time()
time_taken = round(et-st,2)
print(f"Execution time  : {time_taken} seconds")