import sqlite3 as sql

baza='nova_baza.db'

konekcija= sql.connect(baza)
kursor= konekcija.cursor()


napravi_table=''' CREATE TABLE  IF NOT EXISTS highscore (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bodovi TEXT NOT NULL,
                ime TEXT NOT NULL)  '''

kursor.execute(napravi_table)
konekcija.commit()
konekcija.close()