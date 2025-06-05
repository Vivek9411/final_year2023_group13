from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

from flask_login import LoginManager, UserMixin
import pandas as pd

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

import os
import glob
from pathlib import Path

# Using os.listdir()
path = "csvv"
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
print(files)

# Database Models
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
        return f'<Food {self.name}>'

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
        return (f"<Food {self.name} >")


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
        return (f"<Food {self.name} >")


# Create database tables
with app.app_context():
    db.create_all()

all_model = {
    'unit':Food_unit,
    'gm':Food_gm,
    'ml':Food_ml,
}

# with app.app_context():
#     db.session.execute(text('DELETE FROM Food_unit'))
#     db.session.commit()


def add_csv(file_path, unit='gm'):
    entries = []
    model = all_model[unit]
    with open(file = file_path, mode='r', newline='') as csv_file:
        all_lines = csv_file.readlines()
        for x in all_lines[1:]:
            line = x.split(",")
            # print(line)
            new_entry = model(name = line[0].lower(), calories = line[1], sugar = line[2],
                               protein = line[3], carbohydrates = line[4], fiber = line[5],
                               sodium = line[6])
            with app.app_context():
                db.session.add(new_entry)
                db.session.commit()
            entries.append(line[0].lower())
        # print(entr)
    print(entries)
    # with app.app_context():
    return entries

entries = add_csv(file_path=f'csvv/cereals_nutrition_100gm.csv')
# for f in files:
#     if 'gm' in f:
#         unit = 'gm'
#     elif 'ml' in f:
#         unit = 'ml'
#     else:
#         unit = 'unit'
#
#     entries = add_csv(file_path=f'csvv/{f}', unit=unit)
#     with open(file= 'names.txt' , mode='a+') as names:
#         names.write(('\n').join(entries))


def view_custom_items():
    with app.app_context():
        items = Food_ml.query.all()
        for item in items:
            print(item)

view_custom_items()
with app.app_context():
    query = Food_ml.query.filter(Food_ml.name == 'milk').one()
    print(query.calories)
# Insert data into the database
# add_csv('csv/fruits_gm.csv', 'gm', 'Fruit')

print("Database updated successfully!")
view_custom_items()

# if __name__ == '__main__':
#     app.run(debug=True)
