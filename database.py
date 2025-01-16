import sqlite3
import os
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initializeaza_baza_de_date(cale_db):
    """
    Inițializează baza de date SQLite pentru stocarea semnăturilor.
    """
    try:
        conn = sqlite3.connect(cale_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semnaturi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cale_imagine TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()
        logging.info("Baza de date a fost inițializată.")
    except sqlite3.Error as e:
        logging.error(f"Eroare la inițializarea bazei de date: {e}")
    finally:
        if conn:
            conn.close()

def adauga_semnatura(cale_db, cale_imagine):
    """
    Adaugă o semnătură în baza de date și returnează ID-ul acesteia.
    """
    if not os.path.exists(cale_imagine):
        logging.error(f"Fișierul {cale_imagine} nu există.")
        return None

    try:
        conn = sqlite3.connect(cale_db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM semnaturi WHERE cale_imagine = ?', (cale_imagine,))
        if cursor.fetchone():
            logging.info(f"Imaginea {cale_imagine} există deja în baza de date.")
            return None

        cursor.execute('INSERT INTO semnaturi (cale_imagine) VALUES (?)', (cale_imagine,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Eroare la adăugarea semnăturii: {e}")
    finally:
        if conn:
            conn.close()

def sterge_semnatura(cale_db, id_semnatura):
    """
    Șterge o semnătură din baza de date după ID și reindexează ID-urile.
    """
    try:
        conn = sqlite3.connect(cale_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM semnaturi WHERE id = ?', (id_semnatura,))
        conn.commit()
        reindexeaza_iduri(conn)
        return True
    except sqlite3.Error as e:
        logging.error(f"Eroare la ștergerea semnăturii: {e}")
        return False
    finally:
        if conn:
            conn.close()

def reindexeaza_iduri(conn):
    """
    Reindexează ID-urile din tabel după ștergerea unei semnături.
    """
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE temp AS SELECT cale_imagine FROM semnaturi ORDER BY id')
    cursor.execute('DROP TABLE semnaturi')
    cursor.execute('CREATE TABLE semnaturi (id INTEGER PRIMARY KEY AUTOINCREMENT, cale_imagine TEXT NOT NULL UNIQUE)')
    cursor.execute('INSERT INTO semnaturi (cale_imagine) SELECT cale_imagine FROM temp')
    cursor.execute('DROP TABLE temp')
    conn.commit()
    logging.info("ID-urile au fost reindexate.")

def verifica_existenta_semnatura(cale_db, cale_imagine):
    """
    Verifică dacă o imagine există deja în baza de date.
    """
    try:
        conn = sqlite3.connect(cale_db)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM semnaturi WHERE cale_imagine = ?', (cale_imagine,))
        return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logging.error(f"Eroare la verificarea existenței semnăturii: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtine_toate_semnaturile(cale_db):
    """
    Returnează toate semnăturile din baza de date.
    """
    try:
        conn = sqlite3.connect(cale_db)
        cursor = conn.cursor()
        cursor.execute('SELECT id, cale_imagine FROM semnaturi ORDER BY id')
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Eroare la obținerea semnăturilor: {e}")
        return []
    finally:
        if conn:
            conn.close()
