from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    
    # User profile data
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    activity_level = db.Column(db.String(20))
    motive = db.Column(db.String(20))  # 'lose', 'maintain', 'gain'
    
    # Relationships
    custom_items = db.relationship('CustomItem', backref='user', lazy=True)
    meals = db.relationship('Meal', backref='user', lazy=True)
    food_logs = db.relationship('FoodLog', backref='user', lazy=True)
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class CustomItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    unit = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fiber = db.Column(db.Float, nullable=False)
    sugar = db.Column(db.Float, nullable=False)
    sodium = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    
    # Relationships
    meal_items = db.relationship('MealItem', backref='custom_item', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='_user_item_uc'),
    )
    
    def __repr__(self):
        return f'<CustomItem {self.name}>'

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    
    # Relationships
    meal_items = db.relationship('MealItem', backref='meal', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Meal {self.name}>'
    
    @property
    def total_calories(self):
        return sum(item.calories_total for item in self.meal_items)
    
    @property
    def total_protein(self):
        return sum(item.protein_total for item in self.meal_items)
    
    @property
    def total_carbs(self):
        return sum(item.carbs_total for item in self.meal_items)
    
    @property
    def total_fiber(self):
        return sum(item.fiber_total for item in self.meal_items)
    
    @property
    def total_sugar(self):
        return sum(item.sugar_total for item in self.meal_items)
    
    @property
    def total_sodium(self):
        return sum(item.sodium_total for item in self.meal_items)

class MealItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    custom_item_id = db.Column(db.Integer, db.ForeignKey('custom_item.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<MealItem {self.id} in Meal {self.meal_id}>'
    
    @property
    def calories_total(self):
        return self.custom_item.calories * (self.quantity / self.custom_item.quantity)
    
    @property
    def protein_total(self):
        return self.custom_item.protein * (self.quantity / self.custom_item.quantity)
    
    @property
    def carbs_total(self):
        return self.custom_item.carbohydrates * (self.quantity / self.custom_item.quantity)
    
    @property
    def fiber_total(self):
        return self.custom_item.fiber * (self.quantity / self.custom_item.quantity)
    
    @property
    def sugar_total(self):
        return self.custom_item.sugar * (self.quantity / self.custom_item.quantity)
    
    @property
    def sodium_total(self):
        return self.custom_item.sodium * (self.quantity / self.custom_item.quantity)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime,default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    only_date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    meal_type = db.Column(db.String(20))  # breakfast, lunch, dinner, snack
    description = db.Column(db.String(500))
    
    # Nutrition information
    name = db.Column(db.String(200))
    quantity = db.Column(db.Float)
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)
    fiber = db.Column(db.Float)
    sugar = db.Column(db.Float)
    sodium = db.Column(db.Float)
    
    # Optional reference to custom item or meal
    custom_item_id = db.Column(db.Integer, db.ForeignKey('custom_item.id'), nullable=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=True)
    
    def __repr__(self):
        return f'<FoodLog {self.id} on {self.date}>'

class ExerciseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime,default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    only_date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).date())
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer)  # In minutes
    calories_burned = db.Column(db.Float)
    description = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<ExerciseLog {self.name} on {self.date}>'
