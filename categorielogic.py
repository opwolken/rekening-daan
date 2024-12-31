# categorielogic.py

import sqlite3
from datetime import datetime
from subcategorielogic import determine_horeca_subcat, determine_vaste_lasten_subcat
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