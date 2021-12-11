# this code does cross matching between two sets of data.
# last edited 11.12.21 by rei cohen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from datetime import datetime


def sphere_distance_fast(RA_1, Dec_1, RA_2, Dec_2):
    Dist = np.arccos(np.sin(Dec_1) * np.sin(Dec_2) + np.cos(Dec_1) * np.cos(Dec_2) * np.cos(RA_1 - RA_2))
    return Dist


# for fake run (search for matches between CLU and CLU+rand() with 9 lines)
# CLU = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\FakeClu1.csv')).loc[:, ['RA', 'DE']].to_numpy())
# trex = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\FakeClu2.csv')).loc[:, ['RA', 'DE']].to_numpy())
# tolerance = (np.linspace(0, 0.002, 10))

CLU = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\CLU.csv')).loc[:, ['RA', 'DE']].to_numpy())
trex = np.radians(pd.read_csv(os.path.join(os.getcwd(), 'data\\trex.csv')).loc[:, ['ra', 'dec']].to_numpy())
tolerance = (np.linspace(0.065, 0.075, 10))

Current_Folder = os.path.join(os.getcwd(), str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
os.mkdir(Current_Folder)
result_vec = []
Selected_Tol_toPlot = tolerance[-1]

for tol in tqdm(tolerance):
    Matches_Text_Tol = open(os.path.join(Current_Folder, "Matches list for tol =  " + str(tol)[0:6] + '.txt'), "w")
    count_match = 0
    for x in range((len(CLU))):
        distance_vec = sphere_distance_fast(CLU[x][0], CLU[x][1], trex[:, 0], trex[:, 1])
        Where_Vec = np.asarray(np.where(distance_vec < tol))[0]
        count_match = count_match + len(Where_Vec)
        for m in Where_Vec:
            Matches_Text_Tol.write(
                "\n" + 'match between clu@' + str(x) + ' RA is ' + str(np.degrees(CLU[x][0]))[0:7] + ' DEC is ' + str(
                    np.degrees(CLU[x][1]))[0:6] + ' and trex@' + str(m) + ' RA is ' + str(np.degrees(trex[m][0]))[0:7]
                + ' DEC is ' + str(np.degrees(trex[m][1]))[0:6] + "\n")
            if tol == Selected_Tol_toPlot:
                plt.plot(np.degrees(CLU[x][0]), np.degrees(CLU[x][1]), 'bs')
                plt.plot(np.degrees(trex[m][0]), np.degrees(trex[m][1]), 'g^')
    result_vec.append(count_match)
    Matches_Text_Tol.close()
plt.xlabel('RA')
plt.ylabel('DEC')
plt.grid()
plt.title('matches for tol = ' + str(Selected_Tol_toPlot) + '.  Blue = CLU, Green = trex')
plt.savefig(os.path.join(Current_Folder, 'scatter.png'), dpi=300)
plt.close()

print(result_vec)

plt.plot(tolerance, result_vec, 'ro')
plt.xlabel('tolerance @ rad')
plt.ylabel('number of cross-match')
plt.grid()
plt.savefig(os.path.join(Current_Folder, 'fig.png'), dpi=300)
