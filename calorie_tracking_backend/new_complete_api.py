from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import spacy
import os

# ─── APP & DB SETUP ─────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# ─── MODELS ────────────────────────────────────────────────────────────────────

class Food_unit(db.Model):
    __tablename__ = 'food_unit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<Food_unit {self.name}>'

class Food_gm(db.Model):
    __tablename__ = 'food_gm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<Food_gm {self.name}>'

class Food_ml(db.Model):
    __tablename__ = 'food_ml'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<Food_ml {self.name}>'

class DairyProduct(db.Model):
    __tablename__ = 'dairy_product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)
    serving_size = db.Column(db.Float, default=0)       # e.g. 100
    single_unit_size = db.Column(db.Float, default=0)    # e.g. 100
    unit = db.Column(db.String(10), default='g')         # 'g' or 'ml'
    unit_to_gm = db.Column(db.Float, default=1.0)        # conversion factor

    def __repr__(self):
        return f'<DairyProduct {self.name}>'


# ─── CREATE/UPDATE ALL TABLES ───────────────────────────────────────────────────
with app.app_context():
    db.create_all()


# ─── NLP SETUP ───────────────────────────────────────────────────────────────────

# Load your custom-trained NER model (must have labels: QUANTITY, PRODUCT)
trained_nlp = spacy.load('custom_ner_model1')


# ─── HELPERS ────────────────────────────────────────────────────────────────────

# Map number words to their numeric values
word_to_number = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40",
    "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80",
    "ninety": "90", "hundred": "100", "dozen": "12", "half": "0.5",
    "quarter": "0.25"
}

def val_extractor(input_text: str) -> int:
    """
    Convert a string like "two" → 2, "10" → 10, or fallback to -1 if unknown.
    """
    input_text = input_text.strip().lower()
    try:
        return int(input_text)
    except ValueError:
        if input_text in word_to_number:
            return int(word_to_number[input_text])
        return -1

def extract_entities(input_text: str):
    """
    Run the custom NER on `input_text` and return a list of dicts:
      [{'Entity': 'milk', 'Label': 'PRODUCT', 'Quantity': '200ml'}, ...]
    """
    doc = trained_nlp(input_text)
    entities = [{'Entity': ent.text, 'Label': ent.label_} for ent in doc.ents]
    result = []
    last_quantity = None

    for ent in entities:
        if ent['Label'] == "QUANTITY":
            last_quantity = ent['Entity']
        elif ent['Label'] == "PRODUCT":
            result.append({'Entity': ent['Entity'], 'Quantity': last_quantity})
            last_quantity = None

    return result


# ─── ROUTE ──────────────────────────────────────────────────────────────────────

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    input_text = data.get("text", "").lower()

    if not input_text:
        return jsonify({"error": "Input text is required"}), 400

    # Step 1: Extract entities (QUANTITY + PRODUCT)
    processed_data = extract_entities(input_text)
    # processed_data example: [{'Entity': 'milk', 'Quantity': '200ml'}, ...]

    results = {}
    missing_keys = {}

    for single_item in processed_data:
        key = single_item['Entity'].strip().lower()
        quantity_raw = single_item.get('Quantity')

        # If no QUANTITY detected, assume "1 unit"
        if quantity_raw is None:
            quantity_raw = "1"

        # Normalize quantity & unit
        quantity_value = None
        serving_unit = None

        # If the raw string contains "g"
        if 'g' in quantity_raw:
            serving_unit = 'g'
            qty_str = quantity_raw.replace('g', '').strip()
            quantity_value = val_extractor(qty_str)

        # If it contains "ml"
        elif 'ml' in quantity_raw:
            serving_unit = 'ml'
            qty_str = quantity_raw.replace('ml', '').strip()
            quantity_value = val_extractor(qty_str)

        # Otherwise treat as "unit"
        else:
            serving_unit = 'unit'
            quantity_value = val_extractor(quantity_raw)

        if quantity_value == -1 or quantity_value is None:
            # Couldn't parse quantity → mark as not found
            results[key] = {
                'value': quantity_raw,
                'result': False,
                'error': 'Invalid quantity'
            }
            continue

        # ── 1) FIRST, try to find in DairyProduct ──────────────────────────────────
        dairy_query = None
        try:
            dairy_query = DairyProduct.query.filter_by(name=key).one_or_none()
        except Exception:
            dairy_query = None

        if dairy_query:
            # Found in DairyProduct table
            # Compute nutrients proportionally:
            # Let `unit_to_gm` be how many grams per 1 “unit” in the CSV.
            # If serving_unit == 'g', divide by 100; if 'ml', also typically divide by 100 (since CSV is per 100g/ml).
            # If 'unit', then quantity_value is number of “units” (which each correspond to single_unit_size).
            if serving_unit == 'g' or serving_unit == 'ml':
                factor = (quantity_value / dairy_query.serving_size)
            else:
                # e.g. "2 units" → each unit is `single_unit_size` grams, so total grams = quantity_value * single_unit_size
                total_grams = quantity_value * dairy_query.single_unit_size
                factor = total_grams / dairy_query.serving_size

            results[key] = {
                'value': quantity_value,
                'result': True,
                'source_table': 'DairyProduct',
                'name': dairy_query.name,
                'calories': round(dairy_query.calories * factor, 2),
                'protein': round(dairy_query.protein * factor, 2),
                'fat': round(dairy_query.fat * factor, 2),
                'sugar': round(dairy_query.sugar * factor, 2),
                'carbohydrates': round(dairy_query.carbohydrates * factor, 2),
                'fiber': round(dairy_query.fiber * factor, 2),
                'sodium': round(dairy_query.sodium * factor, 2),
                'quantity': f"{quantity_value}{serving_unit}"
            }
            continue

        # ── 2) FALLBACK: search Food_gm, Food_ml, or Food_unit ─────────────────────
        query_obj = None
        try:
            if serving_unit == 'g':
                query_obj = Food_gm.query.filter_by(name=key).one_or_none()
            elif serving_unit == 'ml':
                query_obj = Food_ml.query.filter_by(name=key).one_or_none()
            else:
                query_obj = Food_unit.query.filter_by(name=key).one_or_none()
        except Exception:
            query_obj = None

        if not query_obj:
            # Not found in any table
            missing_keys[key] = {
                'quantity': quantity_value,
                'serving_unit': serving_unit,
                'food': key
            }
            continue

        # If found in one of the old tables:
        # Adjust by factor = quantity_value / 100 for 'g' or 'ml'; factor = quantity_value otherwise.
        if serving_unit in ('g', 'ml'):
            factor = quantity_value / 100
        else:
            factor = quantity_value

        results[key] = {
            'value': quantity_value,
            'result': True,
            'source_table': query_obj.__tablename__,
            'name': query_obj.name,
            'calories': round(query_obj.calories * factor, 2),
            'protein': round(query_obj.protein * factor, 2),
            'sugar': round(query_obj.sugar * factor, 2),
            'carbohydrates': round(query_obj.carbohydrates * factor, 2),
            'fiber': round(query_obj.fiber * factor, 2),
            'sodium': round(query_obj.sodium * factor, 2),
            'quantity': f"{quantity_value}{serving_unit}"
        }
    print(results, missing_keys, 'backend')

    return jsonify({"found": results, "missing": missing_keys})



# ─── RUN FLASK ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
