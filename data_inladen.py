import os
import glob
import sqlite3
import pandas as pd
import re

# 1. Connectie met database
conn = sqlite3.connect("transacties.db")
try:
    cursor = conn.cursor()

    # 2a. Maak de tabel transacties (als die nog niet bestaat) + UNIQUE constraint
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Datum TEXT NOT NULL,
        Omschrijving TEXT NOT NULL,
        Bedrag REAL NOT NULL,
        Categorie TEXT,
        Mededelingen TEXT,
        Beschrijving TEXT,
        Tijdstip TEXT,
        CONSTRAINT unique_transaction UNIQUE (Datum, Omschrijving, Bedrag, Mededelingen)
    );
    """)
    conn.commit()

    # 2b. Maak de tabel categorieen als deze nog niet bestaat
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_transacties_omschrijving
    ON transacties (Omschrijving);
    """)
    conn.commit()

    # 3. Zoek naar alle .csv bestanden in ./rekeningen die beginnen met "NL37INGB"
    bestandspad_pattern = "./rekeningen/NL37INGB*.csv"
    csv_files = glob.glob(bestandspad_pattern)

    # 4. Functies

    # 4.1 functie om bedrag positief of negatief te maken
    def bepaal_bedrag(rij):
        """Return bedrag als float, positief bij 'Bij', negatief bij 'Af'."""
        bedrag_raw = rij["Bedrag (EUR)"].replace(",", ".")
        try:
            bedrag_float = float(bedrag_raw)
        except:
            bedrag_float = 0.0

        if rij["Af Bij"].strip().lower() == "bij":
            return bedrag_float
        else:
            return -bedrag_float

    # 4.2 Mededelingen splitsen
    def parse_mededeling(mededeling: str):
        """
        Haal uit 'mededeling':
        - Beschrijving: tekst na 'Omschrijving:' tot de volgende 'Xxxx:' of einde
        - Tijdstip: HH:MM of HH:MM:SS als dat ergens voorkomt, maar retourneer alleen HH:MM
        """
        if not isinstance(mededeling, str):
            return (None, None)
        
        beschrijving = None
        tijdstip = None
        
        match_beschrijving = re.search(
            r"Omschrijving:\s*(.*?)(?=\s+\w+:|$)",
            mededeling,
            flags=re.IGNORECASE
        )
        if match_beschrijving:
            beschrijving = match_beschrijving.group(1).strip()
        
        match_time = re.search(r"\d{1,2}:\d{2}(?::\d{2})?", mededeling)
        if match_time:
            tijdstip = match_time.group(0)[:5]
        
        return (beschrijving, tijdstip)

    for csv_file in csv_files:
        print(f"Verwerk bestand: {csv_file}")

        df = pd.read_csv(
            csv_file,
            sep=';',          
            quotechar='"',    
            encoding='utf-8', 
            dtype=str
        )

        df["Datum"] = pd.to_datetime(df["Datum"], format="%Y%m%d", errors="coerce")

        df_transacties = pd.DataFrame({
            "Datum": df["Datum"],
            "Omschrijving": df["Naam / Omschrijving"],
            "Bedrag": df.apply(bepaal_bedrag, axis=1),
            "Categorie": None, 
            "Mededelingen": df["Mededelingen"]
        })

        df_transacties["Beschrijving"], df_transacties["Tijdstip"] = zip(
            *df_transacties["Mededelingen"].apply(parse_mededeling)
        )

        df_transacties.dropna(subset=["Datum"], inplace=True)

        for _, row in df_transacties.iterrows():
            datum_str = row["Datum"].strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT OR IGNORE INTO transacties 
                (Datum, Omschrijving, Bedrag, Categorie, Mededelingen, Beschrijving, Tijdstip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datum_str,
                row["Omschrijving"],
                row["Bedrag"],
                row["Categorie"],
                row["Mededelingen"],
                row["Beschrijving"],
                row["Tijdstip"]
            ))
        
        conn.commit()
        print(f"{len(df_transacties)} rijen verwerkt uit {csv_file}.")

    print(df_transacties)

    # 3. Voeg nieuwe omschrijvingen toe uit 'transacties' die nog niet in 'categorieen' staan
    cursor.execute("""
    INSERT OR IGNORE INTO categorieen (Omschrijving)
    SELECT DISTINCT Omschrijving
    FROM transacties
    """)
    conn.commit()

    # 4. Update Bedrag (de som van alle transacties), Aantal en LaatsteDatum 
    #    voor elke Omschrijving in categorieen
    cursor.execute("""
    WITH stats AS (
        SELECT 
            Omschrijving,
            SUM(Bedrag) AS total,
            COUNT(*) AS cnt,
            MAX(Datum) AS last_date
        FROM transacties
        GROUP BY Omschrijving
    )
    UPDATE categorieen
    SET Bedrag = COALESCE((
            SELECT total
            FROM stats s
            WHERE s.Omschrijving = categorieen.Omschrijving
        ), 0),
        Aantal = (
            SELECT cnt
            FROM stats s
            WHERE s.Omschrijving = categorieen.Omschrijving
        ),
        LaatsteDatum = (
            SELECT last_date
            FROM stats s
            WHERE s.Omschrijving = categorieen.Omschrijving
        );
    """)
    conn.commit()

    # 5. Update de saldi van de lopende rekening en de spaarrekening
    cursor.execute("""
    INSERT OR REPLACE INTO saldi (Rekening, Saldo)
    VALUES 
        ('Lopende rekening', 400.79),
        ('Spaarrekening', 9319.75)
    """)
    conn.commit()
finally:
    conn.close()
