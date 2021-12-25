from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
from sklearn.cluster import KMeans
import math
import os

num_of_clusters_in_clu = 7

Results_Folder = os.path.join(os.getcwd(), 'CLU to chandra ' + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
os.mkdir(Results_Folder)


plt.subplot(111, projection="aitoff")
CLU = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\CLU.csv')).loc[:, ['RA', 'DE']].to_numpy())

# use kmeans
km = KMeans(n_clusters=num_of_clusters_in_clu, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
y_km = km.fit_predict(CLU)

# print the clusters
for i in range(num_of_clusters_in_clu):
    plt.scatter(CLU[y_km == i, 0] - math.pi, CLU[y_km == i, 1], label=str('cluster ' + str(i)))
plt.legend(scatterpoints=1)
plt.grid()

# print the centers
plt.scatter(
    km.cluster_centers_[:, 0] - math.pi, km.cluster_centers_[:, 1],
    s=250, marker='*',
    c='red', edgecolor='black',
    label='centroids'
)
print(np.degrees(km.cluster_centers_))
plt.savefig(os.path.join(Results_Folder, 'kmeans.png'), dpi=300)

# save the csv file to upload to chandra
header = ['ra', 'dec']

with open(os.path.join(Results_Folder, 'Upload_to_chandra.csv'), 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(np.degrees(km.cluster_centers_))