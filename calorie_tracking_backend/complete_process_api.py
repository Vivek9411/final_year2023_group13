from flask import Flask, request, jsonify
from sqlalchemy import create_engine, MetaData, Table
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from symspellpy import SymSpell, Verbosity
import json

# Dictionary to map quantity words to numbers
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




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class Food_unit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<Food {self.name} >'

class Food_gm(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)

    def __repr__(self):
        return (f"<Food {self.name} ({self.unit})>")


class Food_ml(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)
    def __repr__(self):
        return (f"<Food {self.name} ({self.unit})>")

# setting up fod nlp
import spacy
trained_nlp = spacy.load('custom_ner_model1')



# extracting food
def extract_entities(input_text):
    doc = trained_nlp(input_text)  # Run NLP model
    entities = [{'Entity': ent.text, 'Label': ent.label_} for ent in doc.ents]  # Convert to list for easier processing
    result = []  # Store final output
    last_quantity = None  # Track last seen QUANTITY

    for ent in entities:
        if ent['Label'] == "QUANTITY":
            last_quantity = ent['Entity']  # Store quantity to assign to next product
        elif ent['Label'] == "PRODUCT":
            result.append({'Entity': ent['Entity'], 'Quantity': last_quantity})
            last_quantity = None  # Reset after assigning to a product
    return result





# # Load SymSpell for spell correction
# sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# sym_spell.load_pickle('new_dictionary.pickle')



# # Function to correct spelling mistakes
# def correct_spelling(input_text):
#     corrected_text = sym_spell.lookup_compound(input_text, max_edit_distance=2)[0].term
#     return corrected_text




# Define table references (Replace with actual table names)
def val_extractor(input_text):
    try:
        temp = int(input_text)
        return temp
    except:
        if input_text.isdigit():
            return int(input_text)
        elif input_text in word_to_number.keys():
            return int(word_to_number[input_text])
        else:
            return -1

@app.route('/process_text', methods=['POST'])
def process_text():
    if request.method == 'POST':
        processed_text = request.get_json()

    data = request.get_json()
    input_text = data.get("text", "").lower()

    if not input_text:
        return jsonify({"error": "Input text is required"}), 400

    # Step 1: Correct spelling mistakes
    # corrected_text = correct_spelling(input_text)
    # print(corrected_text)

    # Step 2: Process input using `extract_entities()`
    processed_data = extract_entities(input_text)
    print(processed_data, 'step1')

    # working
    # Step 3: Check for missing keys in the database
    missing_keys = {}
    results = {}

    for single_item in processed_data:
        key = single_item['Entity'].strip().lower()  # Normalize input
        value = single_item.get('Quantity')  # Default to '1' if missing
        print(key, value, 'step2')
        if value is None:
            value = '1'

        found = False
        quantity = None
        if 'g' in value:
            quantity = 'g'
            value = value.replace('g', "").strip()
            value = val_extractor(value)
            try:
                query = Food_gm.query.filter(Food_gm.name == key).one()
            except Exception as e:
                print(e)
                missing_keys[key]={
                'quantity': value,
                'serving_unit': quantity,
                'food': key
                }
                continue

        elif 'ml' in value:
            quantity = 'ml'
            print('ml', key, value)
            value = value.replace('ml', "").strip()
            value = val_extractor(value)
            try:
                query = Food_ml.query.filter(Food_ml.name == key).one()
            except Exception as e:
                print(e)
                # missing_keys.append(key)
                missing_keys[key]={
                'quantity': value,
                'serving_unit': quantity,
                'food': key
                }
                continue

        else:
            quantity = 'unit'
            value = val_extractor(value)
            print('unit', key, value)
            # value = value.replace('g', "").strip()
            try:
                query = Food_unit.query.filter(Food_unit.name == key).one()
            except Exception as e:
                print(e)
                missing_keys[key]={
                'quantity': value,
                'serving_unit': quantity,
                'food': key
                }
                continue


        value = val_extractor(value)
        print(value)
        if value == -1:
            results[key] = {
                'value': value,
                'result': False
            }
            found = True
        else:
            # if query:
            to_divide = 1 if quantity == 'unit' else 100;
            if query:
                results[key] = {
                    'value': value,
                    'result': True,
                    'name': query.name,
                    'calories': int(query.calories*value/to_divide) ,
                    'protein': int(query.protein*value/to_divide),
                    'sugar': int(query.sugar*value/to_divide),
                    'carbohydrates': int(query.carbohydrates*value/to_divide),
                'fiber': int(query.fiber*value/to_divide),
                'sodium': int(query.sodium*value/to_divide),
                'quantity':quantity
            }
    print(results, missing_keys, 'backend')
    return jsonify({"found": results, "missing": missing_keys})


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug =True, port=5001)  # Run on port 5000
