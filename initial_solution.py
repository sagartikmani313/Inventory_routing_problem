import demand_supply_files_processing as dsfp
# import data_processing as dp
# import plant_supplier_distances as psd
import pandas as pd
import numpy as np
import time

st = time.time()

cluster_importance = dsfp.cluster_importance

et=time.time()
time_taken = round(et-st,2)
print(f"Execution time: {time_taken} seconds")

