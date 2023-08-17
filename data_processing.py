import pandas as pd
import numpy as np
import time
# import plant_supplier_distances as psd

# st = time.time()
def get_cluster_file(filename,sheetname):
   
    clusters = pd.read_excel(filename,sheet_name=sheetname)
    clusters.drop(clusters.iloc[:,5:],inplace=True,axis=1)
    clusters.fillna(0,inplace=True)
    clusters = clusters.astype(np.int64)
    return clusters

def get_supplier_file(filename,sheetname):
    suppliers = pd.read_excel(filename,sheet_name=sheetname)
    suppliers.fillna(0,inplace=True)
    suppliers = suppliers.astype(np.int64)
    supplier_sublist = suppliers.drop(columns=["supplier id","index of supplier","region","number of clusters containing the supplier"])
    return suppliers, supplier_sublist
# cluster_file = get_cluster_file("region_3_compiled.xlsx","cluster_and_supplierID")
# supplier_file, supplier_sublist = get_supplier_file("region_3_compiled.xlsx","suppliers_and_clusterID")



# filling the matrix with ones where the supplier is present in the cluster

def fill_matrix(list_of_suppliers,cluster_id,number_of_clusters):
    #initialising the matrix
    mat = np.zeros([list_of_suppliers,number_of_clusters],dtype=int)
    for i in range(list_of_suppliers):
            for j in range(len(cluster_id.columns)):
                if cluster_id.iloc[i,j] !=0:
                    mat[i,cluster_id.iloc[i,j]-1]=1
    return mat

# A = fill_matrix(len(supplier_file),supplier_sublist,len(cluster_file))


def save_matrix(clusters,suppliers,matrix):
    # creating a dataframe for the matrix and saving it as an excel file
    col_names = np.array([])
    for i in range(clusters):
          col_names = np.append(col_names,f"cluster_id_{i+1}")
    row_names = np.array([])
    for i in range(suppliers):
          row_names = np.append(row_names,f"supplier_{i+1}")

    cluster_matrix = pd.DataFrame(matrix,columns=col_names,index=row_names)
    cluster_matrix.to_excel("cluster_matrix.xlsx",sheet_name="cluster_matrix")


# et=time.time()
# time_taken = round(et-st,2)
# print(f"Execution time  : {time_taken} seconds")
