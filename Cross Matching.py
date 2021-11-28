import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def sphere_distance_fast(RA_1, Dec_1, RA_2, Dec_2):
    Dist = np.arccos(np.sin(Dec_1) * np.sin(Dec_2) + np.cos(Dec_1) * np.cos(Dec_2) * np.cos(RA_1 - RA_2))
    return Dist


CLU = np.radians(pd.read_csv('CLU.csv').loc[:, ['RA', 'DE']].to_numpy())
trex = np.radians(pd.read_csv('trex.csv').loc[:, ['ra', 'dec']].to_numpy())

tolerance = (np.linspace(0.05, 0.1, 20))
result_vec = np.zeros(len(tolerance))

count_int = 0
for tol in tolerance:
    count_match = 0
    for x in range((len(CLU))):
        print('run number ' + str(count_int) + ' @ ' + str(x / len(CLU) * 100)[0:3] + ' %')
        for y in range((len(trex))):
            if sphere_distance_fast(CLU[x][0], CLU[x][1], trex[y][0], trex[y][1]) <= tol:
                count_match = count_match + 1
    result_vec[count_int] = count_match
    count_int = count_int + 1

print(result_vec)

plt.plot(tolerance, result_vec, 'ro')
plt.xlabel('tolerance @ rad')
plt.ylabel('number of cross-match')
plt.savefig('fig.png')
plt.show()
