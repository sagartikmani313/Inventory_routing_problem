import pandas as pd
import numpy as np
# import time
# import plant_supplier_distances as psd

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

def fill_matrix(no_of_suppliers,cluster_id,number_of_clusters):
    #initialising the matrix
    mat = np.zeros([no_of_suppliers,number_of_clusters],dtype=int)
    for i in range(no_of_suppliers):
            for j in range(len(cluster_id.columns)):
                if cluster_id.iloc[i,j]!=0:
                    mat[i,cluster_id.iloc[i,j]-1]=1
    mat = pd.DataFrame(mat)
    mat.index = np.arange(1, no_of_suppliers+1)
    mat.columns = np.arange(1, number_of_clusters+1)
    mat.to_excel("cluster_matrix.xlsx")
    return mat

