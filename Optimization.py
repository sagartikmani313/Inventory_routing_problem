#getting the data structures
#Change id of clusters in cluster_new to start from 1 to len(cluster_new)
cluster2 = {c+1: cluster_new[key] for c, key in enumerate(cluster_new)}
print(cluster2)
C=len(cluster2)

#Objective 2:minimize the number of suppliers in shortage subject the plant capacity
#Initializing model

print(demandfile)


S=56    #The number of suppliers
P=1 #Number of plant
V=[i for i in range(1,S+1)] #The list of suppliers 
A=[(i,j) for i in V for j in V if i!=j] #The list of arcs of suppliers
K=13.4 #The truck capacity in linear meters
N=30    #The number of product types
W=4 #The number of weeks
T=29 #Time horizon





#import demandfile as dictionary using supplier,day and pack as keys and the rest as values except the last column
demandfilecopy=pd.read_excel(Demandfile)
demandfile_dict = demandfilecopy.set_index(['Supplier', 'day', 'pack']).to_dict(orient='index')
print(demandfile_dict)

print(demandfile_dict)

#Create initiatl stock dictionary and put initial stock of suppliers only in cluster2
stock_supplier={(i,j,t):[0,0,0] for i in range(1,S+1) for j in range(1,N+1) for t in range(1,T+1)}
for i in range(1, S+1):
    for j in range(1, N+1):
        for t in range(1, T+1):
            if (i, t, j) in demandfile_dict:
                       stock_supplier[i, j, t][0] = demandfile_dict[i, t, j]['stock init']
                       stock_supplier[i, j, t][1] = demandfile_dict[i, t, j]['stockinitlm']
                       stock_supplier[i, j, t][2] = demandfile_dict[i, t, j]['stockinitinstacks']
                        
print(stock_supplier)

#create a dictionary of the need of suppliers only in cluster2
need={(i,j,t):[0,0,0] for i in range(1,S+1) for j in range(1,N+1) for t in range(1,T+1)}
for i in range(1, S+1):
    for j in range(1, N+1):
        for t in range(1, T+1):
            if (i, t, j) in demandfile_dict:
                need[i, j, t][0] = demandfile_dict[i, t, j]['need']
                need[i, j, t][1] = demandfile_dict[i, t, j]['needlm']
                need[i, j, t][2] = demandfile_dict[i, t, j]['needinstacks']
print(demandfile_dict)

#create a dictionary of stockmin of suppliers only in cluster2
stockmin={(i,j,t):[0,0,0] for i in range(1,S+1) for j in range(1,N+1) for t in range(1,T+1)}
for i in range(1, S+1):
    for j in range(1, N+1):
        for t in range(1, T+1):
            if (i, t, j) in demandfile_dict:
                stockmin[i, j, t][0] = demandfile_dict[i, t, j]['stock min']
                stockmin[i, j, t][1] = demandfile_dict[i, t, j]['stockminlm']
                stockmin[i, j, t][2] = demandfile_dict[i, t, j]['stockmininstacks']
print(stockmin)



#Create a dictionary file for shipment in packaging,linear meter and stacks which will be the decision variables
shipment_out={(p,c,i,j,t):[0,0,0] for p in range(1,P+1) for c in range(1,C+1) for i in range(1,S+1) for j in range(1,N+1) for t in range(1,T+1)}

#Create a dictionary file for shipment in packaging,linear meter and stacks which will be the decision variables
shipment_in={(p,c,i,j,t):[0,0,0]for p in range(1,P+1)  for c in range(1,C+1) for i in cluster2[c] for j in range(1,N+1) for t in range(1,T+1) if cluster2[c][i]==1}
#Import plantfile as dictionary using plant,day and pack as keys and the rest as values
plantfilecopy=pd.read_excel(Plantfile)
print(plantfilecopy)
plantfile_dict = plantfilecopy.set_index(['plant', 'day', 'pack']).to_dict(orient='index')
print(plantfile_dict)

#Create a dictionary for linear meter of every packaging type and the amount that makes a stack
pack_lm={j:[0,0] for j in range(1,N+1)}
for j in range(1,N+1):
    pack_lm[j][0]=plantfile_dict[1,1,j]['linear meter']
    pack_lm[j][1]=plantfile_dict[1,1,j]['number of stack']
print(pack_lm)


#Create a dictionary of the plant intial stock
stock_plant={(i,j,t):[0,0,0] for i in range(1,P+1) for j in range(1,N+1) for t in range(1,T+1)}
for i in range(1, P+1):
    for j in range(1, N+1):
        for t in range(1, T+1):
            if (i, t, j) in plantfile_dict:
                stock_plant[i, j, t][0] = plantfile_dict[i, t, j]['stock init']
                stock_plant[i, j, t][1] = plantfile_dict[i, t, j]['stockinitlm']
                stock_plant[i, j, t][2] = plantfile_dict[i, t, j]['stockinitstacks']
print(stock_plant)

#Create a dictionary of the plant release
release={(p,j,t):[0,0,0] for p in range(1,P+1) for j in range(1,N+1) for t in range(1,T+1)}


#get the position of supplier in a cluster where the supplier is in the cluster
cluster_suppliers={c:[i for i in range(1,S+1) if cluster2[c][i]==1] for c in range(1,C+1)}
position_in_cluster={c:{i:cluster_suppliers[c].index(i)+1 for i in cluster_suppliers[c]} for c in range(1,C+1)}
print(position_in_cluster)
#create a lead time dictionary such that it depends on distance and the position in a route
Leadtime = {(i, j, l): 0 for i in range(1, P + 1) for j in range(1, S + 1) for l in range(1, 4)}
for i in range(1, P + 1):
    for j in range(1, S + 1):
        for l in range(1, 4):
            for c in cluster2:
                items = list(position_in_cluster[c].items())

                # If there is at least one supplier in the cluster
                if len(items) > 0:
                    P1 = items[0][0]
                    
                    # If there are at least two suppliers in the cluster
                    if len(items) > 1:
                        P2 = items[1][0]

                        if cluster2[c][j] == 1 and position_in_cluster[c][j] == 1 and l == 1:
                            if distance_plant2suppliers[i][j] <= 500:
                                Leadtime[i, j, l] = 1
                            elif distance_plant2suppliers[i][j] <= 1050:
                                Leadtime[i, j, l] = 2
                            else:
                                Leadtime[i, j, l] = 3

                        elif cluster2[c][j] == 1 and position_in_cluster[c][j] == 2 and l == 2:
                            if distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][j] <= 500:
                                Leadtime[i, j, l] = 1
                            elif distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][j] <= 1050:
                                Leadtime[i, j, l] = 2
                            else:
                                Leadtime[i, j, l] = math.ceil((distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][j] / 550))

                        elif cluster2[c][j] == 1 and position_in_cluster[c][j] == 3 and l == 3:
                            if distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][P2] + distance_supplier2supplier[P2][j] <= 500:
                                Leadtime[i, j, l] = 1
                            elif distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][P2] + distance_supplier2supplier[P2][j] <= 1050:
                                Leadtime[i, j, l] = 2
                            else:
                                Leadtime[i, j, l] = math.ceil((distance_plant2suppliers[i][P1] + distance_supplier2supplier[P1][P2] + distance_supplier2supplier[P2][j] / 550))
                                
                    # If there's only one supplier in the cluster
                    else:
                        if cluster2[c][j] == 1 and position_in_cluster[c][j] == 1 and l == 1:
                            if distance_plant2suppliers[i][j] <= 500:
                                Leadtime[i, j, l] = 1
                            elif distance_plant2suppliers[i][j] <= 1050:
                                Leadtime[i, j, l] = 2
                            else:
                                Leadtime[i, j, l] = 3

print(Leadtime)


#Optimization models 2: Minimizing number of suppliers in shortage

Time_Plant=[2]+[2+5*f for f in range(1,6)]
print(Time_Plant)
#Initializing model
model = LpProblem(name="Supplier_Shortage Minimization", sense=LpMinimize)
#Initializing variables
shipment_out=LpVariable.dicts("shipment_out",[(p,c,i,j,t) for p in range(1,P+1) for c in range(1,C+1) for i in cluster2[c] for j in range(1,N+1) for t in Time_Plant if cluster2[c][i]==1],lowBound=0,cat='Integer')
y=LpVariable.dicts("shortage",range(1,S+1),lowBound=0,cat='Binary')
print(shipment_out)
#Objective is to know how much to ship in to minimise the number of suppliers in shortage for all product types in the time horizon
model += lpSum(y[i] for i in range(1,S+1))
#Constraints
#big M constraint
big_M=1000

#Shipmentout to every supplier in a cluster must be less than or equal plant capcity
for p in range(1, P+1):
    for t in range(1, T+1):  
        for j in range(1, N+1):
            if t in Time_Plant:
                model += lpSum(shipment_out[(p, c, i, j, t)]  for c in range(1, C+1) for i in cluster2[c] if cluster2[c][i]==1) <= stock_plant[(p,j,t)][2]               
#Stock constraints
for p in range(1, P+1):
    for t in range(1, T+1):
        for j in range(1, N+1):
            # Calculate the release amount
            release[(p,j,t)][2] = lpSum(need[(i,j,max(1,t-timelead_supplier2plant[(p,i)]))][2] for i in range(1,S+1))
            if t in Time_Plant: 
            # Update the plant's stock
                model += stock_plant[(p,j,t)][2] == stock_plant[(p,j,t-1)][2] + release[(p,j,t)][2] - lpSum(shipment_out[(p,c,i,j,t)] for c in range(1, C+1) for i in cluster2[c] if cluster2[c][i]==1)

#Shortage constraints
for c in range(1,C+1):
    for i in cluster2[c]:
        for t in Time_Plant:
            for j in range(1,N+1):
                for p in range(1,P+1):
                    if cluster2[c][i]==1 and l==position_in_cluster[c][i]:                                          
                        model += stock_supplier[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2]== stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2] + shipment_out[(p,c,i,j,t)] - need[(i,j,t+(Leadtime[(p,i,l)]))][2]
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] <= 2*stockmin[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2]
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] >= stockmin[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2]+ y[i]*big_M 
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] >= 0
#Capacity constrshipment_in
for p in range(1,P+1):
    for t in Time_Plant:
        for c in range(1,C+1):
            model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) <= suitable_truck_capacity[c]
            if stablerout_y_or_n[c]==1:
                model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) >= suitable_truck_capacity[c]*0.821    
            else:
                model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) >= suitable_truck_capacity[c]*0.224 

#Solving model       
model.solve()




#Objecttive 3: Minimize shortage and distance
model = LpProblem(name="Supplier_Shortage Minimization", sense=LpMinimize)
#Initializing variables
x=LpVariable.dicts("shipment_out",[(p, c, i, j, t) for p in range(1, P+1) for c in range(1, C+1) for i in cluster2[c] for t in Time_Plant for j in range(1, N+1) if cluster2[c][i] == 1],lowBound=0, cat='Integer')
print(x)
#Objective is to know how much to ship in to minimise the number of suppliers in shortage for all product types in the time horizon
model += lpSum(stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2] + x[(p,c,i,j,t)] - need[(i,j,t+(Leadtime[(p,i,l)]))][2] -stockmin[(i,j,tmin(29,t+1+(Leadtime[(p,i,l)])))][2] for c in range(1,C+1) for i in range(1,S+1) for t in range(1,T+1) for j in range(1,N+1) if cluster2[c][i]==1 and l==position_in_cluster[c][i])
#Constraints
#Shipmentin to every supplier in a cluster must be less than or equal plant capcity
for p in range(1, P+1):
    for t in range(1, T+1):  
        for j in range(1, N+1):
            if t in Time_Plant:
                model += lpSum(x[(p, c, i, j, t)]  for c in range(1, C+1) for i in cluster2[c] if cluster2[c][i]==1) <= stock_plant[p, j, t-1][2]
#Stock constraints
for p in range(1, P+1):
    for t in range(2,T+1):
        for j in range(1, N+1):
            # Calculate the release amount
            release[(p,j,t)][2] = lpSum(need[(i,j,max(1,t-timelead_supplier2plant[(p,i)]))][2] for i in range(1,S+1))
            if t in Time_Plant:
            # Update the plant's stock
                model += stock_plant[(p,j,t)][2] == stock_plant[(p,j,t-1)][2] + release[(p,j,t)][2] - lpSum(x[(p,c,i,j,t)] for c in range(1, C+1) for i in cluster2[c] if cluster2[c]==1)

#Shortage constraints
for c in range(1,C+1):
    for i in cluster2[c]:
        for t in Time_Plant:
            for j in range(1,N+1):
                for p in range(1,P+1):
                    if cluster2[c][i]==1 and l==position_in_cluster[c][i]:                                     
                        model += stock_supplier[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2]== stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2] + x[(p,c,i,j,t)] - need[(i,j,t+(Leadtime[(p,i,l)]))][2]
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+x[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] <= 2*stockmin[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2]
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+x[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] >= stockmin[(i,j,min(29,t+1+(Leadtime[(p,i,l)])))][2] 
                        model += stock_supplier[(i,j,t+(Leadtime[(p,i,l)]))][2]+x[(p,c,i,j,t)]- need[(i,j,t+(Leadtime[(p,i,l)]))][2] >= 0

#Capacity constrshipment_in
for p in range(1,P+1):
    for t in Time_Plant:
        for c in range(1,C+1):
            model += lpSum(x[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) <= suitable_truck_capacity[c]
            if stablerout_y_or_n[c]==1:
                model += lpSum(x[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) >= suitable_truck_capacity[c]*0.821    
            else:
                model += lpSum(x[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in cluster2[c] for j in range(1,N+1) if cluster2[c]==1) >= suitable_truck_capacity[c]*0.224 
#Solving model       
model.solve()




#Working with small sample data
#New cluster
NC=[1,2,17]
Suppliers=[20,2,28,31,34]
Plant=[1]


print(cluster2)
new_cluster={c:cluster2[c] for c in cluster2 if c in NC}
print(new_cluster)  

stock_supplier_new={(i,j,t):[0,0,0] for i in Suppliers for j in range(1,6) for t in range(1,6)}
for i in Suppliers:
    for j in range(1,6):
        for t in range(1,6):
            if (i, t, j) in demandfile_dict:
                       stock_supplier_new[i, j, t][0] = demandfile_dict[i, t, j]['stock init']
                       stock_supplier_new[i, j, t][1] = demandfile_dict[i, t, j]['stockinitlm']
                       stock_supplier_new[i, j, t][2] = demandfile_dict[i, t, j]['stockinitinstacks']
print(stock_supplier_new)

#create a dictionary of the need of suppliers only in cluster2
need_new={(i,j,t):[0,0,0] for i in Suppliers for j in range(1,6) for t in range(1,6)}
for i in Suppliers:
    for j in range(1,6):
        for t in range(1,6):
            if (i, t, j) in demandfile_dict:
                need_new[i, j, t][0] = demandfile_dict[i, t, j]['need']
                need_new[i, j, t][1] = demandfile_dict[i, t, j]['needlm']
                need_new[i, j, t][2] = demandfile_dict[i, t, j]['needinstacks']
print(need_new)

#create a dictionary of stockmin of suppliers only in cluster2
stockmin_new={(i,j,t):[0,0,0] for i in Suppliers for j in range(1,6) for t in range(1,6)}
for i in Suppliers:
    for j in range(1,6):
        for t in range(1,6):
            if (i, t, j) in demandfile_dict:
                stockmin_new[i, j, t][0] = demandfile_dict[i, t, j]['stock min']
                stockmin_new[i, j, t][1] = demandfile_dict[i, t, j]['stockminlm']
                stockmin_new[i, j, t][2] = demandfile_dict[i, t, j]['stockmininstacks']
print(stockmin_new)
#release
release_new={(p,j,t):[0,0,0] for p in Plant for j in range(1,6) for t in range(1,6)}
print(release_new)


#Plant stock file
stock_plant_new={(i,j,t):[0,0,0] for i in Plant for j in range(1,6) for t in range(1,6)}
for i in Plant:
    for j in range(1,6):
        for t in range(1,6):
            if (i, t, j) in plantfile_dict:
                stock_plant_new[i, j, t][0] = plantfile_dict[i, t, j]['stock init']
                stock_plant_new[i, j, t][1] = plantfile_dict[i, t, j]['stockinitlm']
                stock_plant_new[i, j, t][2] = plantfile_dict[i, t, j]['stockinitstacks']
print(stock_plant_new)
print(timelead_supplier2plant)
timelead_supplier2plant_new={(p,j):0 for p in Plant for j in Suppliers}
for p in Plant:
    for j in Suppliers:
        timelead_supplier2plant_new[(p,j)]=timelead_supplier2plant[p,j]
print(timelead_supplier2plant_new)
print(Leadtime)
Leadtime_new={(i, j, l): 0 for i in Plant for j in Suppliers for l in range(1, 4)}
for i in Plant:
    for j in Suppliers:
        for l in range(1, 4):
            Leadtime_new[i,j,l]=Leadtime[i,j,l]
print(Leadtime_new)


#Update stock
#for plant
for p in Plant:
    for t in range(2,6):
        for j in range(1,6):
            stock_plant_new[(p,j,t)][2]+=stock_plant_new[(p,j,t-1)][2]+release_new[(p,j,t)][2]
print(stock_plant_new)
print(release_new)

            
print(stock_plant_new)
#for supplier
for i in Suppliers:
    for t in range(2,6):
        for j in range(1,6):
            stock_supplier_new[(i,j,t)][2]+=stock_supplier_new[(i,j,t-1)][2]-need_new[(i,j,t-1)][2]
            
print(stock_supplier_new)



#Optimization models: Minimizing number of suppliers in shortage
#Define a function that minimizes the number of suppliers in shortage
Time_Plant=[2]
print(Time_Plant)
#Initializing model
model = LpProblem(name="Supplier_Shortage Minimization", sense=LpMinimize)
#Initializing variables
shipment_out=LpVariable.dicts("shipment_out",[(p,c,i,j,t) for p in Plant for c in NC for i in new_cluster[c] for j in range(1,6) for t in Time_Plant if new_cluster[c][i]==1],lowBound=0,cat='Integer')
z = LpVariable.dicts("shortage_indicator", [(i,j,t) for i in Suppliers for j in range(1,6) for t in Time_Plant], cat='Binary')

#Objective is to know how much to ship in to minimise the number of suppliers in shortage for all product types in the time horizon
model += lpSum(z[(i,j,t)] for i in Suppliers)
#Constraints
#big M constraint
big_M=100

#Shipmentout to every supplier in a cluster must be less than or equal plant capcity
for p in Plant:
    for t in Time_Plant:  
        for j in range(1, 6):            
            model += lpSum(shipment_out[(p, c, i, j, t)]  for c in new_cluster for i in new_cluster[c] if new_cluster[c][i]==1) <= stock_plant_new[(p,j,t-1)][2]               
#Stock constraints
for p in Plant:
    for t in Time_Plant:
        for j in range(1, 6):            
            model += stock_plant_new[(p,j,t)][2] == stock_plant_new[(p,j,t-1)][2] - lpSum(shipment_out[(p,c,i,j,t)] for c in new_cluster for i in new_cluster[c] if new_cluster[c][i]==1)

#Shortage constraints
for c in new_cluster:
    for i in new_cluster[c]:
        for t in Plant:
            for j in range(1,6):
                for p in Plant:
                    if t in Time_Plant and new_cluster[c][i]==1 and l==position_in_cluster[c][i]:                       
                        model += stock_supplier_new[(i,j,t+(Leadtime_new[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)] <= 2*stockmin_new[(i,j,min(5,t+1+(Leadtime_new[(p,i,l)])))][2]
                        model += stock_supplier_new[(i,j,t+(Leadtime_new[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)] >= stockmin_new[(i,j,min(5,t+1+(Leadtime_new[(p,i,l)])))][2]+ z[(i,j,t)]*big_M                        
                        model += stock_supplier_new[(i,j,t+(Leadtime_new[(p,i,l)]))][2]+shipment_out[(p,c,i,j,t)] >= 0

#Capacity constrshipment_in
for p in Plant:
    for t in Time_Plant:
        for c in new_cluster:
            model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in new_cluster[c] for j in range(1,6) if new_cluster[c][i]==1) <= suitable_truck_capacity[c]
            if stablerout_y_or_n[c]==1:
                model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in new_cluster[c] for j in range(1,N+1) if new_cluster[c][i]==1) >= suitable_truck_capacity[c]*0.821    
            else:
                model += lpSum(shipment_out[(p,c,i,j,t)]*pack_lm[j][0]*pack_lm[j][1] for i in new_cluster[c] for j in range(1,N+1) if new_cluster[c][i]==1) >= suitable_truck_capacity[c]*0.224 

#Solving model       
model.solve()
