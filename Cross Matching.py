# this code does cross matching between two sets of data.
# last edited 21.3.22 by rei cohen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import math


def sphere_distance_fast(RA_1, Dec_1, RA_2, Dec_2):
    Dist = np.arccos(np.sin(Dec_1) * np.sin(Dec_2) + np.cos(Dec_1) * np.cos(Dec_2) * np.cos(RA_1 - RA_2))
    return Dist


Catalog1 = 'data\\CLU.csv'
Catalog2 = 'data\\Trex_LONG_near_CLU.pkl'

Catalog1_Name = Catalog1[5:-4]
Catalog2_Name = Catalog2[5:-4]

Catalog1_Parameters = ['RA', 'DE', 'Name']
Catalog2_Parameters = ['ra', 'dec', 'ObsID', 't_i', 't_f', 'S/N', 'mean_d_optical_arcmin', 'Chandra_counterpart',
                       'photons_in_ap_info', 'grating', 'nrows', 'buffer_pixels', 'chipx_avg', 'chipy_avg']

# Read the csv files

Catalog1_Data = pd.read_csv(os.path.join(os.getcwd(), Catalog1)).loc[:, Catalog1_Parameters]
Catalog2_Data = pd.read_pickle(os.path.join(os.getcwd(), Catalog2)).loc[:, Catalog2_Parameters]
Catalog2_Data = Catalog2_Data.loc[Catalog2_Data['ra'] != 'N/A']

# change degrees to rad
Catalog1_Data['RA'] = np.radians(Catalog1_Data['RA'].to_numpy())
Catalog1_Data['DE'] = np.radians(Catalog1_Data['DE'].to_numpy())
Catalog2_Data['ra'] = Catalog2_Data['ra'].astype(float) * math.pi / 180
Catalog2_Data['dec'] = Catalog2_Data['dec'].astype(float) * math.pi / 180

#conditions by maayane
pixel_size = 0.492
cond_noHETGLETG = Catalog2_Data['grating'] == 'NONE'
dfx = Catalog2_Data[cond_noHETGLETG]
cond_nosubarrays = dfx['nrows'] > 1000
cond_non_buffer = dfx['buffer_pixels'] == 0
cond_no_border = (dfx['chipx_avg'] > 16 / pixel_size) & (dfx['chipx_avg'] < 1024 - 16 / pixel_size) & (
        dfx['chipy_avg'] > 16 / pixel_size) & (dfx['chipy_avg'] < 1024 - 16 / pixel_size)
cond_have_photons = dfx['photons_in_ap_info'] != '[]'
Trex_cat = dfx[cond_nosubarrays & cond_no_border & cond_non_buffer]
Catalog2_Data = Trex_cat.reset_index(drop=True)

# Define the angular tolerance
tolerance = 10 * (2 * math.pi / 1296000)

# Create Folders
Results_Folder = os.path.join(os.getcwd(), Catalog1_Name + ' && ' + Catalog2_Name + ' @ ' + str(
    datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
Results_Folder_for_LC = os.path.join(Results_Folder, 'LC')
os.mkdir(Results_Folder)
os.mkdir(Results_Folder_for_LC)


#do the Cross Matching
M = []
X = []
for x in range((len(Catalog1_Data))):
    distance_vec = sphere_distance_fast(Catalog1_Data.iloc[x, 0], Catalog1_Data.iloc[x, 1], Catalog2_Data.iloc[:, 0],
                                        Catalog2_Data.iloc[:, 1])
    Where_Vec = np.asarray(np.where(distance_vec < tolerance))[0]
    for m in Where_Vec:
        X.append(x)
        M.append(m)

#save the sub catalog that contain only the matches
Catalog1_Matches = Catalog1_Data.iloc[X].reset_index(drop=True)
Catalog2_Matches = Catalog2_Data.iloc[M].reset_index(drop=True)

#save the data for SkyViewer format
Catalog1_to_sky = pd.DataFrame(
    {'ra': np.degrees(Catalog1_Matches.iloc[:, 0]), 'dec': np.degrees(Catalog1_Matches.iloc[:, 1]), 'name': X,
     'color': 'blue', 'radius': 10})
Catalog2_to_sky = pd.DataFrame(
    {'ra': np.degrees(Catalog2_Matches.iloc[:, 0]), 'dec': np.degrees(Catalog2_Matches.iloc[:, 1]), 'name': M,
     'color': 'green', 'radius': 10, 'photons_in_ap_info': Catalog2_Matches['photons_in_ap_info']})
To_Sky = Catalog1_to_sky.merge(Catalog2_to_sky, how='outer')
To_Sky.to_csv(os.path.join(Results_Folder, Catalog1_Name + ' && ' + Catalog2_Name + '.csv'), index=False)

#save the Light Curve plots
for i in range(len(Catalog2_Matches)):
    photons = pd.DataFrame(Catalog2_Matches['photons_in_ap_info'][i], columns=['time', 'x', 'y', 'energy'])
    plt.figure(1)
    n, bins, patches = plt.hist(photons['time'], bins=50)
    bins_centers = 0.5 * (bins[:-1] + bins[1:])
    plt.xlabel('photons arrival times [s]')
    plt.ylabel('Number of photons')
    plt.grid()
    plt.savefig(os.path.join(Results_Folder_for_LC, 'Hist Trex' + str(i) + '.png'), facecolor='w', edgecolor='w',
                orientation='portrait', format='png',
                transparent=False, bbox_inches=None, pad_inches=0.1)
    plt.close()

