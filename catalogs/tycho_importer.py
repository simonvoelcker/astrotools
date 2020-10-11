import sqlite3
import os


def create_db(conn):
    conn.execute('''
        CREATE TABLE stars (
            tycid TEXT NOT NULL,
            ra REAL NOT NULL,
            dec REAL NOT NULL,
            vtmag REAL,
            btmag REAL,
            mag REAL NOT NULL
        );
    ''')
    conn.execute('CREATE INDEX radecindex ON stars (ra, dec);')
    conn.execute('CREATE INDEX magindex ON stars (mag);')
    conn.commit()


def populate_db(conn, src_file):
    with open(src_file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            columns = line.split('|')
            if len(columns) != 32:
                print("WARN: Unexpected column count. Skipping line")
                continue

            tyc_id = line[0:12]
            ra = float(line[152:164])
            dec = float(line[165:177])

            vt_mag = line[123:129].strip()
            bt_mag = line[110:116].strip()
            mag = float(vt_mag) if vt_mag else float(bt_mag)

            if not ra or not dec or not mag:
                print("WARN: Incomplete data. Skipping line")

            params = (tyc_id, ra, dec, vt_mag, bt_mag, mag)
            conn.execute('INSERT INTO stars VALUES (?,?,?,?,?,?);', params)

        conn.commit()


directory = '/home/simon/Hobby/astro/Tycho-2/'
src_file = os.path.join(directory, 'catalog.dat')
db_file = os.path.join(directory, 'tycho2.db')

connection = sqlite3.connect(db_file)
create_db(connection)
populate_db(connection, src_file)
connection.close()
