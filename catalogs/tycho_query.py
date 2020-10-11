import sqlite3
import os

directory = '/home/simon/Hobby/astro/Tycho-2/'
src_file = os.path.join(directory, 'catalog.dat')
db_file = os.path.join(directory, 'tycho2.db')

connection = sqlite3.connect(db_file)

result = connection.execute('''
    SELECT *
    FROM stars
    WHERE dec > 0 AND dec < 10 AND ra > 0 AND ra < 10
    ORDER BY mag
    LIMIT 10
    OFFSET 100
''')

for row in result:
    print(row)

connection.close()
