import sqlite3
import os

directory = '/home/simon/Hobby/astro/Tycho-2/'
src_file = os.path.join(directory, 'catalog.dat')
db_file = os.path.join(directory, 'tycho2.db')

connection = sqlite3.connect(db_file)

result = connection.execute('''
    SELECT *
    FROM stars
    ORDER BY mag
    LIMIT 25000
''')

import numpy as np
import matplotlib.pyplot as plt

xs = []
ys = []
for row in result:
    xs.append(row[1])
    ys.append(row[2])

xs = np.array(xs)
ys = np.array(ys)

plt.scatter(xs, ys, s=1, c='#000000', alpha=0.3)
plt.title('Stars')
plt.xlabel('RA')
plt.ylabel('Dec')
plt.savefig('starplot.png', dpi=400)

connection.close()
