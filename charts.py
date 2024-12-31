import sqlite3
from datetime import datetime

def get_data_uren_van_dag(db_path):
    """
    Voorbeeld: tel aantal transacties (of som van bedragen) per uur van de dag.
    Geeft twee lijsten terug: 'labels' (uren 0..23) en 'data' (bijv. totale uitgave).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT substr(Tijdstip, 1, 2) as uur, SUM(Bedrag)
        FROM transacties
        WHERE Tijdstip != ''
        GROUP BY uur
        ORDER BY uur
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = []
    data = []
    for uur, bedrag_sum in rows:
        if uur is not None:
            labels.append(uur)  # "00", "01", ..., "23"
            data.append(round(abs(bedrag_sum), 2))  # abs() als 'Af' negatief is

    return labels, data

def get_data_top10(db_path):
    """
    Geeft (labels, data) van de 10 'duurste' Omschrijvingen.
    Let op: we sorteren op SUM(Bedrag) oplopend (negatief = uitgave),
    of we nemen abs(...) om 'hoogste uitgave' te krijgen.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Omschrijving, SUM(Bedrag) as total
        FROM transacties
        GROUP BY Omschrijving
        ORDER BY SUM(Bedrag) ASC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = []
    data = []
    for oms, val in rows:
        labels.append(oms)
        data.append(round(abs(val), 2))  # absolute waarde van de uitgave

    return labels, data

def get_data_spaartrend(db_path):
    """
    Haal per maand de som van alle Bedrag waar Categorie='Sparen'.
    Bouw daar een cumulatieve trend van.
    Voeg een tweede lijn toe met het periodegemiddelde van 3 maanden.
    Retourneert (labels, data, avg_data).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m-01', Datum) as maand, SUM(Bedrag)
        FROM transacties
        WHERE Categorie = 'Sparen'
        GROUP BY maand
        ORDER BY maand
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = []
    data = []
    avg_data = []
    running_total = 0.0

    for maand, val in rows:
        running_total += val
        labels.append(maand[:7])  # "YYYY-MM"
        data.append(round(running_total, 2))

    # Bereken het periodegemiddelde van 3 maanden
    for i in range(len(data)):
        if i < 2:
            avg_data.append(None)  # Niet genoeg data voor een gemiddelde
        else:
            avg_data.append(round(sum(data[i-2:i+1]) / 3, 2))

    return labels, data, avg_data

def get_data_inkomen(db_path):
    """
    Haal per maand de som van alle Bedrag waar Categorie='Inkomen'.
    Bouw daar een gestapelde bar chart van met subcategorieën.
    Voeg een tweede lijn toe met het 12-maanden gemiddelde.
    Retourneert (labels, datasets, avg_data, saldi).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m-01', Datum) as maand, COALESCE(Subcategorie, 'Geen subcategorie') as subcat, SUM(Bedrag)
        FROM transacties
        WHERE Categorie = 'Inkomen'
        GROUP BY maand, subcat
        ORDER BY maand, subcat
    """)
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT Rekening, Saldo
        FROM saldi
    """)
    saldi_rows = cursor.fetchall()
    conn.close()

    labels = sorted(list(set(row[0][:7] for row in rows)))  # "YYYY-MM"
    subcats = sorted(list(set(row[1] for row in rows)))

    data_dict = {subcat: [0] * len(labels) for subcat in subcats}
    for maand, subcat, val in rows:
        index = labels.index(maand[:7])
        data_dict[subcat][index] = round(val, 2)

    datasets = []
    for subcat, data in data_dict.items():
        datasets.append({
            "label": subcat,
            "data": data,
            "backgroundColor": f"rgba({hash(subcat) % 256}, {(hash(subcat) // 256) % 256}, {(hash(subcat) // 65536) % 256}, 0.6)"
        })

    # Bereken het 12-maanden gemiddelde
    total_data = [sum(data_dict[subcat][i] for subcat in subcats) for i in range(len(labels))]
    avg_data = []
    for i in range(len(total_data)):
        if i < 11:
            avg_data.append(None)  # Niet genoeg data voor een gemiddelde
        else:
            avg_data.append(round(sum(total_data[i-11:i+1]) / 12, 2))

    saldi = {row[0]: row[1] for row in saldi_rows}

    return labels, datasets, avg_data, saldi

def get_yearly_inkomen(db_path):
    """
    Haal per jaar de som van alle Bedrag waar Categorie='Inkomen'.
    Bouw daar een gestapelde bar chart van met subcategorieën.
    Voeg een tweede lijn toe met het 12-maanden gemiddelde.
    Retourneert (labels, datasets, avg_data).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y', Datum) as jaar, COALESCE(Subcategorie, 'Geen subcategorie') as subcat, SUM(Bedrag)
        FROM transacties
        WHERE Categorie = 'Inkomen'
        GROUP BY jaar, subcat
        ORDER BY jaar, subcat
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = sorted(list(set(row[0] for row in rows)))  # "YYYY"
    subcats = sorted(list(set(row[1] for row in rows)))

    data_dict = {subcat: [0] * len(labels) for subcat in subcats}
    for jaar, subcat, val in rows:
        index = labels.index(jaar)
        data_dict[subcat][index] = round(val, 2)

    datasets = []
    for subcat, data in data_dict.items():
        datasets.append({
            "label": subcat,
            "data": data,
            "backgroundColor": f"rgba({hash(subcat) % 256}, {(hash(subcat) // 256) % 256}, {(hash(subcat) // 65536) % 256}, 0.6)"
        })

    # Bereken het 12-maanden gemiddelde
    total_data = [sum(data_dict[subcat][i] for subcat in subcats) for i in range(len(labels))]
    avg_data = []
    for i in range(len(total_data)):
        if i < 11:
            avg_data.append(None)  # Niet genoeg data voor een gemiddelde
        else:
            avg_data.append(round(sum(total_data[i-11:i+1]) / 12, 2))

    return labels, datasets, avg_data

def get_categorieen_per_jaar(db_path):
    """
    Haal per jaar de gemiddelde maandelijkse uitgaven per categorie op.
    Retourneert (labels, datasets).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y', Datum) as jaar, Categorie, SUM(Bedrag) / 12 as avg_per_month
        FROM transacties
        WHERE Categorie IS NOT NULL
        GROUP BY jaar, Categorie
        ORDER BY jaar, Categorie
    """)
    rows = cursor.fetchall()
    conn.close()

    labels = sorted(list(set(row[0] for row in rows)))  # "YYYY"
    categories = sorted(list(set(row[1] for row in rows)))

    data_dict = {category: [0] * len(labels) for category in categories}
    for jaar, category, avg_per_month in rows:
        index = labels.index(jaar)
        data_dict[category][index] = round(avg_per_month, 2)

    datasets = []
    for category, data in data_dict.items():
        datasets.append({
            "label": category,
            "data": data,
            "backgroundColor": f"rgba({hash(category) % 256}, {(hash(category) // 256) % 256}, {(hash(category) // 65536) % 256}, 0.6)"
        })

    return labels, datasets