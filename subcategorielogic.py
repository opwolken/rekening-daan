from datetime import datetime
import sqlite3
import time

def determine_horeca_subcat(time_str: str, default_subcat: str):
    """
    Als time_str bestaat en valide is:
      - 04:00 <= tijd < 10:30 -> 'ontbijt'
      - 10:30 <= tijd < 15:00 -> 'lunch'
      - 15:00 <= tijd < 18:30 -> 'borrel'
      - anders -> 'diner'
    Als geen tijd, hou default_subcat of 'Horeca'
    """
    if not time_str or time_str.strip() == "":
        return default_subcat or "Horeca"
    
    t = None
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.strptime(time_str.strip(), fmt).time()
            break
        except ValueError:
            continue
    
    if t is None:
        # Kon niet parsen
        return default_subcat or "Horeca"
    
    hm = t.hour * 60 + t.minute  # totaal aantal minuten vanaf middernacht
    
    if 240 <= hm < 630:   # tussen 04:00 en 10:30
        return "Ontbijt"
    elif 630 <= hm < 900:  # tussen 10:30 en 15:00
        return "Lunch"
    elif 900 <= hm < 1110: # tussen 15:00 en 18:30
        return "Borrel"
    else:
        return "Diner"

def determine_vaste_lasten_subcat(db_path: str):
    """
    Bepaal de subcategorie 'Vaste lasten' voor transacties binnen de categorie 'Financiën'
    met omschrijving die begint met 'hummel%blom' en waarbij de kolom 'Tijdstip' leeg is.
    """
    retries = 5
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            try:
                cursor = conn.cursor()

                # Update transacties binnen de categorie 'Financiën' met omschrijving die bevat '%hummel%blom%' en Tijdstip is NULL
                cursor.execute("""
                    UPDATE transacties
                    SET Subcategorie = 'Vaste lasten'
                    WHERE Categorie = 'Financiën' AND Omschrijving LIKE '%hummel%blom%' AND (Tijdstip IS NULL OR Tijdstip = '')
                """)

                conn.commit()
            finally:
                conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries -= 1
                time.sleep(1)
            else:
                raise
