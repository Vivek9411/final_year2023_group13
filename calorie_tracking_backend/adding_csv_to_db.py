from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import csv

# ─── APP & DB SETUP ─────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# ─── MODEL DEFINITION ───────────────────────────────────────────────────────────

class DairyProduct(db.Model):
    __tablename__ = 'dairy_product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)
    serving_size = db.Column(db.Float, default=0)
    single_unit_size = db.Column(db.Float, default=0)
    unit = db.Column(db.String(10), default='')
    unit_to_gm = db.Column(db.Float, default=1.0)

    def __repr__(self):
        return f"<DairyProduct {self.name}>"


# ─── ENSURE TABLE EXISTS ────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()


# ─── CSV INSERT FUNCTION ────────────────────────────────────────────────────────
def insert_csv(file_path):
    """
    Reads a single CSV file and bulk-inserts into DairyProduct. 
    Splits any name with parentheses into two entries (e.g. "Curd (Dahi)" → "Curd" and "Dahi").
    """
    print(f"→ Processing file: {file_path!r}")
    rows_inserted = 0

    with app.app_context():
        # Open and read CSV
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_rows = list(reader)

        print(f"  • Found {len(all_rows)} data rows (excluding header).")

        for row in all_rows:
            raw_name = row.get('name', '').strip()
            if not raw_name:
                # Skip any blank line or missing-name row
                continue

            # Build a list of one or two names if parentheses are present
            names_to_insert = [raw_name]
            if '(' in raw_name and ')' in raw_name:
                before = raw_name.split('(')[0].strip()
                inside = raw_name.split('(')[1].replace(')', '').strip()
                # Overwrite with the split names
                names_to_insert = [before, inside]

            # For each name (maybe two if parentheses), create a model instance
            for name_variant in names_to_insert:
                try:
                    dp = DairyProduct(
                        name=name_variant.lower(),
                        calories=float(row.get('calories', 0)),
                        protein=float(row.get('protein', 0)),
                        carbohydrates=float(row.get('carbohydrates', 0)),
                        fiber=float(row.get('fiber', 0)),
                        fat=float(row.get('fat', 0)),
                        sugar=float(row.get('sugar', 0)),
                        sodium=float(row.get('sodium', 0)),
                        serving_size=float(row.get('serving_size', 0)),
                        single_unit_size=float(row.get('single_unit_size', 0)),
                        unit=row.get('unit', '').strip().lower(),
                        unit_to_gm=float(row.get('unit_to_gm', 1.0))
                    )
                except ValueError as e:
                    print(f"    ✖ Skipping row due to parse error: {e!r} (row: {row})")
                    continue

                db.session.add(dp)
                rows_inserted += 1

        # Commit once after all rows for this file have been `add()`ed
        db.session.commit()
        print(f"  ✔ Committed {rows_inserted} rows from {os.path.basename(file_path)}\n")


# ─── LOOP THROUGH ALL *.CSV IN `csvv/` ─────────────────────────────────────────
if __name__ == '__main__':
    folder_path = 'csv_files'
    if not os.path.isdir(folder_path):
        print(f"Error: folder {folder_path!r} does not exist. Make sure your CSV files live in ./csvv/")
    else:
        csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
        if not csv_files:
            print(f"Error: no .csv files found in {folder_path!r}")
        else:
            for fname in csv_files:
                path = os.path.join(folder_path, fname)
                insert_csv(path)

            print("✅ All CSV files have been processed.")
