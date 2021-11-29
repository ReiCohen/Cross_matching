import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def sphere_distance_fast(RA_1, Dec_1, RA_2, Dec_2):
    Dist = np.arccos(np.sin(Dec_1) * np.sin(Dec_2) + np.cos(Dec_1) * np.cos(Dec_2) * np.cos(RA_1 - RA_2))
    return Dist


CLU = np.radians(pd.read_csv('CLU.csv').loc[:, ['RA', 'DE']].to_numpy())
trex = np.radians(pd.read_csv('trex.csv').loc[:, ['ra', 'dec']].to_numpy())

tolerance = (np.linspace(0.0675, 0.07, 22))
result_vec = []

for tol in tqdm(tolerance):
    count_match = 0
    for x in range((len(CLU))):
        distance_vec = sphere_distance_fast(CLU[x][0], CLU[x][1], trex[:, 0], trex[:, 1])
        count_match = count_match + len(distance_vec[distance_vec < tol])
    result_vec.append(count_match)

print(result_vec)

plt.plot(tolerance, result_vec, 'ro')
plt.xlabel('tolerance @ rad')
plt.ylabel('number of cross-match')
plt.savefig('fig.png')
plt.grid()
plt.show()
