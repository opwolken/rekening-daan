print("Loading my_routes.py...")

from flask import render_template, request, redirect, url_for, jsonify
import sqlite3
from categorielogic import update_all_transactions
from charts import get_data_uren_van_dag, get_data_spaartrend, get_data_inkomen, get_data_top10, get_yearly_inkomen, get_categorieen_per_jaar

DB_PATH = "transacties.db"  # Pas aan als jouw db anders heet

def init_routes(app):
    print("Defining init_routes...")

    @app.route('/')
    def index():
        return redirect(url_for('dashboard'))

    @app.route('/categorize', methods=['GET', 'POST'])
    def categorize():
        if request.method == 'POST':
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            for key, value in request.form.items():
                if key.startswith('cat_'):
                    omschrijving = key.replace('cat_', '')
                    nieuwe_categorie = value.strip()
                    if nieuwe_categorie:
                        cursor.execute("""
                            UPDATE categorieen
                            SET Categorie = ?
                            WHERE Omschrijving = ?
                        """, (nieuwe_categorie, omschrijving))
            conn.commit()
            conn.close()
            return redirect(url_for('categorize'))
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Omschrijving, Bedrag, Aantal, LaatsteDatum
                FROM categorieen
                WHERE Categorie IS NULL OR Categorie = ''
                ORDER BY Bedrag ASC, LaatsteDatum DESC, Aantal Desc
                LIMIT 10
            """)
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM categorieen")
            total_rows = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM categorieen WHERE Categorie IS NULL OR Categorie = ''")
            uncategorized_rows = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM transacties")
            total_trans_rows = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM transacties WHERE Categorie IS NULL OR Categorie = ''")
            uncategorized_trans_rows = cursor.fetchone()[0]
            conn.close()
            return render_template('categorize.html', rows=rows, total_trans_rows=total_trans_rows, uncategorized_trans_rows=uncategorized_trans_rows, total_rows=total_rows, uncategorized_rows=uncategorized_rows)

    @app.route('/categories', methods=['GET', 'POST'])
    def categories():
        if request.method == 'POST':
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            for key, value in request.form.items():
                if key.startswith('cat_'):
                    old_category = key.replace('cat_', '')
                    new_category = value.strip()
                    if new_category:
                        cursor.execute("""
                            UPDATE categorieen
                            SET Categorie = ?
                            WHERE Categorie = ?
                        """, (new_category, old_category))
            conn.commit()
            conn.close()
            return redirect(url_for('categories'))
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Categorie, COUNT(*) as count
                FROM categorieen
                WHERE Categorie IS NOT NULL AND Categorie != ''
                GROUP BY Categorie
                ORDER BY count DESC
            """)
            categories = cursor.fetchall()
            conn.close()
            return render_template('categories.html', categories=categories)

    @app.route('/specify', methods=['GET', 'POST'])
    def specify():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if request.method == 'POST':
            for key, value in request.form.items():
                if key.startswith('subcat_'):
                    omschrijving = key.replace('subcat_', '')
                    subcategorie = value.strip()
                    if subcategorie:
                        cursor.execute("""
                            UPDATE categorieen
                            SET Subcategorie = ?
                            WHERE Omschrijving = ?
                        """, (subcategorie, omschrijving))
                        cursor.execute("""
                            UPDATE transacties
                            SET Subcategorie = ?
                            WHERE Omschrijving = ?
                        """, (subcategorie, omschrijving))
            conn.commit()
            conn.close()
            return redirect(url_for('specify'))
        cursor.execute("""
            SELECT DISTINCT Categorie
            FROM categorieen
            WHERE Categorie IS NOT NULL AND Categorie != ''
        """)
        categories = [row[0] for row in cursor.fetchall()]
        selected_category = request.args.get('category', categories[0] if categories else None)
        if selected_category:
            cursor.execute("""
                SELECT Omschrijving, Subcategorie
                FROM categorieen
                WHERE Categorie = ?
            """, (selected_category,))
            rows = cursor.fetchall()
        else:
            rows = []
        conn.close()
        return render_template('specify.html', categories=categories, selected_category=selected_category, rows=rows)

    @app.route('/update_transactions', methods=['GET', 'POST'])
    def update_transactions():
        if request.method == 'POST':
            update_all_transactions(DB_PATH)
            return redirect(url_for('categorize'))
        else:
            return render_template('update_transactions.html')

    @app.route("/dashboard")
    def dashboard():
        uren_labels, uren_data = get_data_uren_van_dag(DB_PATH)
        spaartrend_labels, spaartrend_data, spaartrend_avg_data = get_data_spaartrend(DB_PATH)
        inkomen_labels, inkomen_datasets, inkomen_avg_data, inkomen_saldi = get_data_inkomen(DB_PATH)
        top10_labels, top10_data = get_data_top10(DB_PATH)
        categorieen_jaar_labels, categorieen_jaar_datasets = get_categorieen_per_jaar(DB_PATH)
        return render_template(
            "dashboard.html",
            uren_labels=uren_labels,
            uren_data=uren_data,
            spaartrend_labels=spaartrend_labels,
            spaartrend_data=spaartrend_data,
            spaartrend_avg_data=spaartrend_avg_data,
            inkomen_labels=inkomen_labels,
            inkomen_datasets=inkomen_datasets,
            inkomen_avg_data=inkomen_avg_data,
            top10_labels=top10_labels,
            top10_data=top10_data,
            categorieen_jaar_labels=categorieen_jaar_labels,
            categorieen_jaar_datasets=categorieen_jaar_datasets,
            inkomen_saldi=inkomen_saldi
        )

    @app.route("/get_monthly_inkomen_data")
    def get_monthly_inkomen_data():
        labels, datasets, avg_data = get_data_inkomen(DB_PATH)
        return jsonify(labels=labels, datasets=datasets, avg_data=avg_data)

    @app.route("/get_yearly_inkomen_data")
    def get_yearly_inkomen_data():
        labels, datasets, avg_data = get_yearly_inkomen(DB_PATH)
        return jsonify(labels=labels, datasets=datasets, avg_data=avg_data)

print("my_routes.py loaded successfully.")