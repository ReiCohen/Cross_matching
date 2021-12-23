# this code does cross matching between two sets of data.
# last edited 23.12.21 by rei cohen
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


# for fake run (search for matches between CLU and CLU+rand() with 9 lines)
# CLU = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\FakeClu1.csv')).loc[:, ['RA', 'DE']].to_numpy())
# trex = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\FakeClu2.csv')).loc[:, ['RA', 'DE']].to_numpy())
# tolerance = (np.linspace(0, 0.002, 10))

# Read the csv files
CLU = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\CLU.csv')).loc[:, ['RA', 'DE']].to_numpy())
trex = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\trex.csv')).loc[:, ['ra', 'dec']].to_numpy())

# Define the angular tolerance
tolerance = (np.linspace(0.065, 0.075, 20))

# Define the angular tolerance for the plots
Selected_Tol_toPlot = tolerance[-1]

# Create Folders
Results_Folder = os.path.join(os.getcwd(), str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
Folder_for_txt = os.path.join(Results_Folder, 'txt')
os.mkdir(Results_Folder)
os.mkdir(Folder_for_txt)


result_vec = []
plt.figure(2)
plt.subplot(projection="aitoff")
plt.grid()

data_for_legacysurvey = []

for tol in tqdm(tolerance):
    Matches_Text_Tol = open(os.path.join(Folder_for_txt, "Matches list for tol =  " + str(tol)[0:6] + '.txt'),
                            "w")
    count_match = 0
    for x in range((len(CLU))):
        distance_vec = sphere_distance_fast(CLU[x][0], CLU[x][1], trex[:, 0], trex[:, 1])
        Where_Vec = np.asarray(np.where(distance_vec < tol))[0]

        # add the number of matches with this tol
        count_match = count_match + len(Where_Vec)

        for m in Where_Vec:
            # save all the matches for each tolerance, in txt file
            Matches_Text_Tol.write(
                "\n" + 'match between clu@' + str(x) + ' RA is ' + str(np.degrees(CLU[x][0]))[0:7] + ' DEC is ' + str(
                    np.degrees(CLU[x][1]))[0:6] + ' and trex@' + str(m) + ' RA is ' + str(np.degrees(trex[m][0]))[0:7]
                + ' DEC is ' + str(np.degrees(trex[m][1]))[0:6] + "\n")
            # save only the matches for tolerance = Selected_Tol_toPlot
            if tol == Selected_Tol_toPlot:
                # plot simple scatter
                plt.figure(1)
                plt.scatter(np.degrees(CLU[x][0]), np.degrees(CLU[x][1]),  facecolors='none', edgecolors='b')
                plt.scatter(np.degrees(trex[m][0]), np.degrees(trex[m][1]), facecolors='g', edgecolors='none')

                # plot 3D scatter
                plt.figure(2)
                plt.scatter(CLU[x][0] - math.pi, CLU[x][1], facecolors='none', edgecolors='b')
                plt.scatter(trex[m][0] - math.pi, trex[m][1], facecolors='g', edgecolors='none')

                # save the ,matches in the data_for_legacysurvey to use later as csv
                data_for_legacysurvey.append(
                    [str(np.degrees(CLU[x][0]))[0:7], str(np.degrees(CLU[x][1]))[0:6], 'clu@' + str(x), 'blue',
                     '10'])
                data_for_legacysurvey.append(
                    [str(np.degrees(trex[m][0]))[0:7], str(np.degrees(trex[m][1]))[0:6], 'trex@' + str(m), 'green',
                     '10'])

    result_vec.append(count_match)
    Matches_Text_Tol.close()

# save the 2d scatter
plt.figure(1)
plt.xlabel('RA')
plt.ylabel('DEC')
plt.grid()
plt.title('matches for tol = ' + str(Selected_Tol_toPlot) + '.  Blue = CLU, Green = trex')
plt.savefig(os.path.join(Results_Folder, 'Scatter.png'), dpi=300)

# save the 3d scatter
plt.figure(2)
plt.title('matches for tol = ' + str(Selected_Tol_toPlot) + '.  Blue = CLU, Green = trex' + "\n")
plt.savefig(os.path.join(Results_Folder, '3D.png'), dpi=300)

# save the MatchesVsTol plot
plt.figure(3)
plt.plot(tolerance, result_vec, 'ro')
plt.xlabel('tolerance @ rad')
plt.ylabel('number of cross-matches')
plt.grid()
plt.savefig(os.path.join(Results_Folder, 'MatchesVsTol.png'), dpi=300)

# save the csv file to upload to legacysurvey
header = ['ra', 'dec', 'name', 'color', 'radius']
with open(os.path.join(Results_Folder, 'Upload_to_legacy_survey.csv'), 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data_for_legacysurvey)
