# this code does cross matching between two sets of data.
# last edited 25.1.22 by rei cohen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from datetime import datetime
import csv
import math


def sphere_distance_fast(RA_1, Dec_1, RA_2, Dec_2):
    Dist = np.arccos(np.sin(Dec_1) * np.sin(Dec_2) + np.cos(Dec_1) * np.cos(Dec_2) * np.cos(RA_1 - RA_2))
    return Dist


Catalog1 = 'data\\CLU.csv'
Catalog2 = 'data\\Trex_LONG_near_CLU.csv'

Catalog1_Name = Catalog1[5:-4]
Catalog2_Name = Catalog2[5:-4]

Catalog1_Parameters = ['RA', 'DE', 'Name']
Catalog2_Parameters = ['ra', 'dec', 'ObsID', 't_i', 't_f', 'S/N', 'mean_d_optical_arcmin', 'Chandra_counterpart',
                       'photons_in_ap_info', 'grating', 'nrows', 'buffer_pixels', 'chipx_avg', 'chipy_avg']

# Read the csv files

Catalog1_Data = pd.read_csv(os.path.join(os.getcwd(), Catalog1)).loc[:, Catalog1_Parameters]
Catalog2_Data = pd.read_csv(os.path.join(os.getcwd(), Catalog2)).loc[:, Catalog2_Parameters]

# change degrees to rad
Catalog1_Data['RA'] = np.radians(Catalog1_Data['RA'].to_numpy())
Catalog1_Data['DE'] = np.radians(Catalog1_Data['DE'].to_numpy())
Catalog2_Data['ra'] = np.radians(Catalog2_Data['ra'].to_numpy())
Catalog2_Data['dec'] = np.radians(Catalog2_Data['dec'].to_numpy())

pixel_size = 0.492

cond_noHETGLETG = Catalog2_Data['grating'] == 'NONE'
dfx = Catalog2_Data[cond_noHETGLETG]
cond_nosubarrays = dfx['nrows'] > 1000
cond_non_buffer = dfx['buffer_pixels'] == 0
cond_no_border = (dfx['chipx_avg'] > 16 / pixel_size) & (dfx['chipx_avg'] < 1024 - 16 / pixel_size) & (
            dfx['chipy_avg'] > 16 / pixel_size) & (dfx['chipy_avg'] < 1024 - 16 / pixel_size)
Trex_cat = dfx[cond_nosubarrays & cond_no_border & cond_non_buffer]
Catalog2_Data = Trex_cat.reset_index(drop=True)
print(Catalog2_Data)

# Define the angular tolerance
tolerance = 10 * (2 * math.pi / 1296000)
tolerance = (np.linspace(tolerance, tolerance, 1))

# Define the angular tolerance for the plots
Selected_Tol_toPlot = tolerance[-1]

# Create Folders
Results_Folder = os.path.join(os.getcwd(), Catalog1_Name + ' && ' + Catalog2_Name + ' @ ' + str(
    datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
Folder_for_txt = os.path.join(Results_Folder, 'txt')
os.mkdir(Results_Folder)
os.mkdir(Folder_for_txt)

result_vec = []
plt.figure(2)
plt.subplot(projection="aitoff")
for i in range((len(Catalog1_Data))):
    plt.scatter(Catalog1_Data.iloc[i, 0] - math.pi, Catalog1_Data.iloc[i, 1], facecolors='none', edgecolors='b',
                linewidth=0.1)
plt.grid()

data_for_legacysurvey = []

for tol in tqdm(tolerance):
    Matches_Text_Tol = open(os.path.join(Folder_for_txt, "Matches list for tol =  " + str(tol)[0:6] + '.txt'),
                            "w")
    count_match = 0
    for x in range((len(Catalog1_Data))):
        distance_vec = sphere_distance_fast(Catalog1_Data.iloc[x, 0], Catalog1_Data.iloc[x, 1],
                                            Catalog2_Data.iloc[:, 0],
                                            Catalog2_Data.iloc[:, 1])
        Where_Vec = np.asarray(np.where(distance_vec < tol))[0]

        # add the number of matches with this tol
        count_match = count_match + len(Where_Vec)

        for m in Where_Vec:
            # save all the matches for each tolerance, in txt file
            Matches_Text_Tol.write(
                "\n" + 'match between ' + Catalog1_Name + '@' + str(x + 2) + ' RA is ' + str(
                    np.degrees(Catalog1_Data.iloc[x, 0]))[0:7] + ' DEC is ' + str(
                    np.degrees(Catalog1_Data.iloc[x, 1]))[0:6] + ' and ' + Catalog2_Name + '@' + str(
                    m + 2) + ' RA is ' + str(
                    np.degrees(Catalog2_Data.iloc[m, 0]))[0:7]
                + ' DEC is ' + str(np.degrees(Catalog2_Data.iloc[m, 1]))[0:6] + "\n")
            # save only the matches for tolerance = Selected_Tol_toPlot
            if tol == Selected_Tol_toPlot:
                # plot simple scatter
                plt.figure(1)
                plt.scatter(np.degrees(Catalog1_Data.iloc[x, 0]), np.degrees(Catalog1_Data.iloc[x, 1]),
                            facecolors='none',
                            edgecolors='b')
                plt.scatter(np.degrees(Catalog2_Data.iloc[m, 0]), np.degrees(Catalog2_Data.iloc[m, 1]), facecolors='g',
                            edgecolors='none')

                # plot 3D scatter
                plt.figure(2)
                plt.scatter(Catalog2_Data.iloc[m, 0] - math.pi, Catalog2_Data.iloc[m, 1], facecolors='g',
                            edgecolors='none', s=20)

                distance_temp = sphere_distance_fast(Catalog1_Data.iloc[x, 0], Catalog1_Data.iloc[x, 1],
                                                     Catalog2_Data.iloc[m, 0],
                                                     Catalog2_Data.iloc[m, 1])
                # save the ,matches in the data_for_legacysurvey to use later as csv
                data_for_legacysurvey.append(
                    [str(np.degrees(Catalog1_Data.iloc[x, 0]))[0:10], str(np.degrees(Catalog1_Data.iloc[x, 1]))[0:10],
                     Catalog1_Name + '@' + str(x + 2), 'blue',
                     '10', Catalog1_Data['Name'][x], '', '', '', '', '', '', ''])
                data_for_legacysurvey.append(
                    [str(np.degrees(Catalog2_Data.iloc[m, 0]))[0:10], str(np.degrees(Catalog2_Data.iloc[m, 1]))[0:10],
                     Catalog2_Name + '@' + str(m + 2), 'green',
                     '10', Catalog2_Data['ObsID'][m], Catalog2_Data['t_i'][m], Catalog2_Data['t_f'][m],
                     Catalog2_Data['S/N'][m], Catalog2_Data['mean_d_optical_arcmin'][m], str(distance_temp),
                     Catalog2_Data['Chandra_counterpart'][m], Catalog2_Data['photons_in_ap_info'][m]])

    result_vec.append(count_match)
    Matches_Text_Tol.close()

# save the 2d scatter
plt.figure(1)
plt.xlabel('RA')
plt.ylabel('DEC')
plt.grid()
plt.title('matches for tol = ' + str(Selected_Tol_toPlot) + '.  Blue = ' + Catalog1_Name + ', Green = ' + Catalog2_Name)
plt.savefig(os.path.join(Results_Folder, 'Scatter.png'), dpi=300)

# save the 3d scatter
plt.figure(2)
plt.title('matches for tol = ' + str(
    Selected_Tol_toPlot) + '.  Blue = ' + Catalog1_Name + ', Green = ' + Catalog2_Name + "\n")
plt.savefig(os.path.join(Results_Folder, '3D.png'), dpi=300)

# save the MatchesVsTol plot
plt.figure(3)
plt.plot(tolerance, result_vec, 'ro')
plt.xlabel('tolerance @ rad')
plt.ylabel('number of cross-matches')
plt.grid()
plt.savefig(os.path.join(Results_Folder, 'MatchesVsTol.png'), dpi=300)

# save the csv file to upload to legacysurvey
header = ['ra', 'dec', 'name', 'color', 'radius', 'info', 't_i', 't_f', 'S/N', 'mean_d_optical_arcmin',
          'dis_to_counter_CLU', 'Chandra_counterpart', 'photons_in_ap_info']
with open(os.path.join(Results_Folder, Catalog1_Name + '_&&_' + Catalog2_Name + '_' + 'UPLOAD_to_legacy_survey.csv'),
          'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data_for_legacysurvey)

Trex_Matches = pd.DataFrame(data_for_legacysurvey[1::2], columns=header)

Trex_Matches_in = Trex_Matches[Trex_Matches['Chandra_counterpart'] != 0]
Trex_Matches_out = Trex_Matches[Trex_Matches['Chandra_counterpart'] == 0]

plt.figure(4)
plt.scatter(Trex_Matches_in['t_i'].astype(float), Trex_Matches_in['S/N'].astype(float), marker='^')
plt.scatter(Trex_Matches_out['t_i'].astype(float), Trex_Matches_out['S/N'].astype(float), marker='o')
plt.grid()
plt.xlabel('t_i')
plt.ylabel('S/N')
plt.title('^ IN, o OUT')
plt.savefig(os.path.join(Results_Folder, '1.png'), dpi=300)

plt.figure(5)
plt.scatter(Trex_Matches_in['dis_to_counter_CLU'].astype(float), Trex_Matches_in['mean_d_optical_arcmin'].astype(float),
            marker='^')
plt.scatter(Trex_Matches_out['dis_to_counter_CLU'].astype(float),
            Trex_Matches_out['mean_d_optical_arcmin'].astype(float),
            marker='o')
plt.grid()
plt.xlabel('dis_to_counter_CLU')
plt.ylabel('mean_d_optical_arcmin')
plt.title('^ IN, o OUT')
plt.savefig(os.path.join(Results_Folder, '2.png'), dpi=300)

with open(os.path.join(Results_Folder,
                       'ONLY TREX ' + Catalog1_Name + '_&&_' + Catalog2_Name + '_' + 'UPLOAD_to_legacy_survey.csv'),
          'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data_for_legacysurvey[1::2])
