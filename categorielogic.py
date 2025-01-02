# categorielogic
import sqlite3
from datetime import datetime
import time

def update_all_transactions(db_path: str):
    """
    Vul in 'transacties' de kolommen Categorie en Subcategorie
    op basis van 'categorieen'.
    Als Categorie='horeca', pas extra tijdstip-logica toe.
    Als Tijdstip leeg is en Omschrijving bevat '%hummel%blom%', zet Subcategorie op 'Vaste lasten'.
    """
    retries = 5
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            try:
                cursor = conn.cursor()
                
                # 1. Haal alle transacties op (id, Omschrijving, Tijdstip)
                cursor.execute("""
                    SELECT id, Omschrijving, Tijdstip
                    FROM transacties
                """)
                trans_rows = cursor.fetchall()  # List of (id, omschrijving, tijdstip)
                
                # Voor elke transactie: kijk in categorieen wat de Categorie/Subcategorie is
                for (t_id, oms, time_str) in trans_rows:
                    # Haal de categorie + subcategorie uit tabel 'categorieen'
                    cursor.execute("""
                        SELECT Categorie, Subcategorie 
                        FROM categorieen 
                        WHERE Omschrijving = ?
                    """, (oms,))
                    row_cat = cursor.fetchone()  # (Categorie, Subcategorie) of None
                    
                    if row_cat is not None:
                        cat, subcat = row_cat  # bv. ("horeca", "algemeen")
                        
                        # 2. Als Tijdstip leeg is en Omschrijving bevat '%hummel%blom%', zet Subcategorie op 'Vaste lasten'
                        if not time_str and 'hummel' in oms.lower() and 'blom' in oms.lower():
                            subcat = 'Vaste lasten'
                        # 3. Als Categorie == 'horeca', doe tijd-logica
                        elif cat is not None and cat.lower() == "horeca" and (subcat is None or subcat.lower() != "bestellen"):
                            # Bepaal de subcategorie op basis van tijd
                            subcat = determine_horeca_subcat(time_str, subcat)
                        
                        # 4. UPDATE de transactie
                        if subcat:
                            cursor.execute("""
                                UPDATE transacties
                                SET Categorie = ?, Subcategorie = ?
                                WHERE id = ?
                            """, (cat, subcat, t_id))
                        else:
                            cursor.execute("""
                                UPDATE transacties
                                SET Categorie = ?
                                WHERE id = ?
                            """, (cat, t_id))
                
                # Pas de logica voor 'Vaste lasten' toe
                determine_vaste_lasten_subcat(db_path)
                
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

#Subcategorie logic: determine_horeca_subcat
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

#Subcategorie logic: determine_vaste_lasten_subcat
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
