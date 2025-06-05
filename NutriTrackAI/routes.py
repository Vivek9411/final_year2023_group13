from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, cast, Date
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, date
from app import app, db
from models import User, CustomItem, Meal, MealItem, FoodLog, ExerciseLog
from forms import RegistrationForm, LoginForm, NaturalLanguageInputForm_Food, CustomItemForm, MealForm, MealItemForm, \
    ProfileForm, NaturalLanguageInputForm_Exercise
from nlp_processor import NLPProcessor
import json
import pytz
from werkzeug.security import generate_password_hash

# Initialize NLP Processor
nlp_processor = NLPProcessor()
tz_ist = pytz.timezone('Asia/Kolkata')
# Custom Jinja filters
@app.template_filter('round_up_to_nearest')
def round_up_to_nearest(value, base):
    return ((value + base - 1) // base) * base

# Home route
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            weight=form.weight.data,
            height=form.height.data,
            age=form.age.data,
            gender=form.gender.data,
            activity_level=form.activity_level.data,
            motive=form.motive.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Main dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    form_food = NaturalLanguageInputForm_Food()
    form_exercise = NaturalLanguageInputForm_Exercise()
    
    # Get today's date and the date range for past week and month
    tz_ist = pytz.timezone('Asia/Kolkata')
    time = datetime.now(tz_ist).time()
    today = datetime.now(tz_ist).date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get user's calorie requirements
    user_has_complete_profile = all([
        current_user.weight, 
        current_user.height, 
        current_user.age, 
        current_user.gender, 
        current_user.activity_level, 
        current_user.motive
    ])
    
    if user_has_complete_profile:
        from nutrition_calculator import get_full_recommendations
        recommendations = get_full_recommendations(current_user)
        target_calories = recommendations['nutrition']['calories']
        target_protein = recommendations['nutrition']['protein']
        target_carbs = recommendations['nutrition']['carbs']
        target_fiber = recommendations['nutrition']['fiber']
        target_sugar = recommendations['nutrition']['sugar']
        target_sodium = recommendations['nutrition']['sodium']
    else:
        # Default values if user hasn't completed their profile
        target_calories = 2000
        target_protein = 50
        target_carbs = 250
        target_fiber = 28
        target_sugar = 50
        target_sodium = 2300

    # FoodLog.query.filter_by(user_id=current_user.id)
    # Calculate today's nutrition summary
    todays_food = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.only_date == today
    ).all()

    # print(1,todays_food)

    today_calories = sum(log.calories for log in todays_food)
    today_protein = sum(log.protein for log in todays_food)
    today_carbs = sum(log.carbohydrates for log in todays_food)
    today_fiber = sum(log.fiber for log in todays_food)
    today_sugar = sum(log.sugar for log in todays_food)
    today_sodium = sum(log.sodium for log in todays_food)

    # Calculate percentages of daily targets
    if target_calories > 0:
        calories_percent = min(round((today_calories / target_calories) * 100), 100)
    else:
        calories_percent = 0
        
    if target_protein > 0:
        protein_percent = min(round((today_protein / target_protein) * 100), 100)
    else:
        protein_percent = 0
        
    if target_carbs > 0:
        carbs_percent = min(round((today_carbs / target_carbs) * 100), 100)
    else:
        carbs_percent = 0
        
    if target_fiber > 0:
        fiber_percent = min(round((today_fiber / target_fiber) * 100), 100)
    else:
        fiber_percent = 0
    
    # Calculate today's exercise summary

    todays_exercise = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date == today
    ).all()
    
    today_calories_burned = sum(log.calories_burned for log in todays_exercise)
    
    # Calculate calorie data for the past week (for chart)
    daily_calories = []
    daily_calories_burned = []
    daily_labels = []
    daily_targets = []
    
    for i in range(7):
        day = today - timedelta(days=6-i)
        daily_labels.append(day.strftime('%a'))
        daily_targets.append(target_calories)
        
        # Food calories for this day
        day_food = FoodLog.query.filter(
            FoodLog.user_id == current_user.id,
            FoodLog.only_date == day
        ).all()
        day_calories = sum(log.calories for log in day_food)
        daily_calories.append(day_calories)
        
        # Exercise calories for this day
        day_exercise = ExerciseLog.query.filter(
            ExerciseLog.user_id == current_user.id,
            ExerciseLog.only_date == day
        ).all()
        day_calories_burned = sum(log.calories_burned for log in day_exercise)
        daily_calories_burned.append(day_calories_burned)
    
    # Get recent food logs
    recent_food_logs = FoodLog.query.filter_by(user_id=current_user.id).order_by(FoodLog.date.desc()).limit(5).all()
    
    # Get recent exercise logs
    recent_exercise_logs = ExerciseLog.query.filter_by(user_id=current_user.id).order_by(ExerciseLog.date.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html', 
        form=form_food,
        exercise_form = form_exercise,
        today_calories=round(today_calories,2),
        today_protein=round(today_protein,2),
        today_carbs=round(today_carbs,2),
        today_fiber=round(today_fiber,2),
        today_sugar=round(today_sugar,2),
        today_sodium=round(today_sodium,2),
        today_calories_burned=round(today_calories_burned,2),
        net_calories=round(today_calories - today_calories_burned,2),
        target_calories=round(target_calories,2),
        target_protein=round(target_protein,2),
        target_carbs=round(target_carbs,2),
        target_fiber=round(target_fiber,2),
        target_sugar=round(target_sugar,2),
        target_sodium=round(target_sodium,2),
        calories_percent=round(calories_percent,2),
        protein_percent=round(protein_percent,2),
        carbs_percent=round(carbs_percent,2),
        fiber_percent=round(fiber_percent,2),
        daily_labels=json.dumps(daily_labels),
        daily_calories=json.dumps(daily_calories),
        daily_calories_burned=json.dumps(daily_calories_burned),
        daily_targets=json.dumps(daily_targets),
        recent_food_logs=recent_food_logs,
        recent_exercise_logs=recent_exercise_logs,
        has_complete_profile=user_has_complete_profile
    )

# Natural language processing routes
@app.route('/process_query', methods=['POST'])
@login_required
def process_food_query():
    form = NaturalLanguageInputForm_Food()
    if form.validate_on_submit():
        query = form.query.data
        
        # First try to process as a food query
        food_results, missing  = nlp_processor.process_food_query(query, current_user.id)
        print(food_results, 'this is the result')
        if food_results or missing:
            for food_result in food_results:

                name = food_result['food']
                if_present = CustomItem.query.filter_by(user_id=current_user.id, name=name).first()
                unit = food_result['serving_unit']
                if if_present and if_present.unit==unit:
                    saved_quantity = if_present.quantity

                    food_log = FoodLog(
                        user_id=current_user.id,
                        name = food_result['food'],
                        quantity=food_result['quantity'],
                        calories=round(if_present.calories*food_result['quantity']/saved_quantity,1),
                        protein=round(if_present.protein*food_result['quantity']/saved_quantity,1),
                        carbohydrates=round(if_present.carbohydrates*food_result['quantity']/saved_quantity,1),
                        fiber=round(if_present.fiber*food_result['quantity']/saved_quantity,1),
                        sugar=round(if_present.sugar*food_result['quantity']/saved_quantity,1),
                        sodium=round(if_present.sodium*food_result['quantity']/saved_quantity,1),
                        date=datetime.now(tz_ist),
                        description=query
                    )
                    print(1)
                    calories = round(if_present.calories*food_result['quantity']/saved_quantity,1)
                else:
                    food_log = FoodLog(
                        user_id=current_user.id,
                        name=food_result['food'],
                        quantity=food_result['quantity'],
                        calories=round(food_result['calories'],1),
                        protein=round(food_result['protein'],1),
                        carbohydrates=round(food_result['carbohydrates'],1),
                        fiber=round(food_result['fiber'],1),
                        sugar=round(food_result['sugar'],1),
                        sodium=round(food_result['sodium'],1),
                        date=datetime.now(tz_ist),
                        description=query
                    )
                    calories=food_result['calories']
                db.session.add(food_log)
                db.session.commit()
                flash(f"Added {food_result['food']} with {calories} calories to your food log!", 'success')
            if missing:
                print(missing)
                for food in missing.keys():
                    food_result= missing[food]
                    name = food_result['food']
                    if_present = CustomItem.query.filter_by(user_id=current_user.id, name=name).first()
                    unit = food_result['serving_unit']
                    if if_present and if_present.unit==unit:
                        saved_quantity = if_present.quantity
                        print('got it ')
                        food_log = FoodLog(
                            user_id=current_user.id,
                            name=food_result['food'],
                            quantity=food_result['quantity'],
                            calories=round(if_present.calories * food_result['quantity'] / saved_quantity, 1),
                            protein=round(if_present.protein * food_result['quantity'] / saved_quantity, 1),
                            carbohydrates=round(if_present.carbohydrates * food_result['quantity'] / saved_quantity, 1),
                            fiber=round(if_present.fiber * food_result['quantity'] / saved_quantity, 1),
                            sugar=round(if_present.sugar * food_result['quantity'] / saved_quantity, 1),
                            sodium=round(if_present.sodium * food_result['quantity'] / saved_quantity, 1),
                            date=datetime.now(tz_ist),
                            description=query
                        )
                        calories= round(if_present.calories * food_result['quantity'] / saved_quantity, 1)
                        db.session.add(food_log)
                        db.session.commit()
                        flash(f"Added {food_result['food']} with {calories} calories to your food log!", 'success')
                    else:
                        print('not found')
                        flash(f"Couldn't find {food} in your food item database. Please add it to your food item database.", 'warning')

            return redirect(url_for('dashboard'))
        else:
            flash("Couldn't understand your input. Please try again with more details.", 'danger')
            return redirect(url_for('dashboard'))
    
    flash('Invalid form submission.', 'danger')
    return redirect(url_for('dashboard'))


# for processing the exercise query
@app.route('/process_exercise_query', methods=['POST'])
@login_required
def process_exercise_query():
    form = NaturalLanguageInputForm_Exercise()
    if form.validate_on_submit():
        query = form.query.data
        exercise_result = nlp_processor.process_exercise_query(user_input=query, gender=current_user.gender, weight=current_user.weight, height=current_user.height,age=current_user.age)
        print(exercise_result)
        if exercise_result:
            # Add to exercise log
            for exercise in exercise_result:
                exercise_log = ExerciseLog(
                        user_id=current_user.id,
                        name=exercise['exercise'],
                        duration=exercise['duration'],
                        calories_burned=exercise['calories'],
                        description=query
                    )
                db.session.add(exercise_log)
                db.session.commit()

                flash(
                    f"Added {exercise['exercise']} burning {exercise['calories']} calories to your exercise log!",
                    'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Couldn't understand your input. Please try again with more details.", 'danger')
            return redirect(url_for('dashboard'))

    flash('Invalid form submission.', 'danger')
    return redirect(url_for('dashboard'))
# Food item management routes
@app.route('/food_items')
@login_required
def food_items():
    form = CustomItemForm()
    items = CustomItem.query.filter_by(user_id=current_user.id).order_by(CustomItem.name).all()
    return render_template('food_items.html', items=items, form=form)


@app.route('/add_food_item', methods=['POST'])
@login_required
def add_food_item():
    form = CustomItemForm()
    if form.validate_on_submit():
        try:
            item = CustomItem(
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data,
                unit=form.unit.data,
                quantity=form.quantity.data,
                calories=form.calories.data,
                protein=form.protein.data,
                carbohydrates=form.carbohydrates.data,
                fiber=form.fiber.data,
                sugar=form.sugar.data,
                sodium=form.sodium.data
            )
            db.session.add(item)
            db.session.commit()
            flash(f'Food item "{form.name.data}" added successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash(f'You already have a food item named "{form.name.data}"', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the food item', 'danger')
            app.logger.error(f"Error adding food item: {str(e)}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('food_items'))

@app.route('/edit_food_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_food_item(item_id):
    item = CustomItem.query.get_or_404(item_id)
    
    # Check if item belongs to the current user
    if item.user_id != current_user.id:
        flash('You are not authorized to edit this item.', 'danger')
        return redirect(url_for('food_items'))
    
    form = CustomItemForm()
    
    if request.method == 'GET':
        form.name.data = item.name
        form.description.data = item.description
        form.unit.data = item.unit
        form.quantity.data = item.quantity
        form.calories.data = item.calories
        form.protein.data = item.protein
        form.carbohydrates.data = item.carbohydrates
        form.fiber.data = item.fiber
        form.sugar.data = item.sugar
        form.sodium.data = item.sodium
    
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.unit = form.unit.data
        item.quantity = form.quantity.data
        item.calories = form.calories.data
        item.protein = form.protein.data
        item.carbohydrates = form.carbohydrates.data
        item.fiber = form.fiber.data
        item.sugar = form.sugar.data
        item.sodium = form.sodium.data
        
        db.session.commit()
        flash(f'Food item "{item.name}" updated successfully!', 'success')
        return redirect(url_for('food_items'))
    
    return render_template('food_items.html', form=form, edit_item=item, items=CustomItem.query.filter_by(user_id=current_user.id).all())

@app.route('/delete_food_item/<int:item_id>', methods=['POST'])
@login_required
def delete_food_item(item_id):
    item = CustomItem.query.get_or_404(item_id)
    
    # Check if item belongs to the current user
    if item.user_id != current_user.id:
        flash('You are not authorized to delete this item.', 'danger')
        return redirect(url_for('food_items'))
    
    db.session.delete(item)
    db.session.commit()
    flash(f'Food item "{item.name}" deleted successfully!', 'success')
    return redirect(url_for('food_items'))

# Meal management routes
@app.route('/meals')
@login_required
def meals():
    meal_form = MealForm()
    meal_item_form = MealItemForm()
    
    # Populate the food item choices for the meal item form
    meal_item_form.custom_item_id.choices = [
        (item.id, f"{item.name} ({item.quantity} {item.unit})")
        for item in CustomItem.query.filter_by(user_id=current_user.id).order_by(CustomItem.name).all()
    ]
    
    meals = Meal.query.filter_by(user_id=current_user.id).order_by(Meal.name).all()
    
    return render_template('meals.html', 
                          meals=meals, 
                          meal_form=meal_form, 
                          meal_item_form=meal_item_form)

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal():
    form = MealForm()
    if form.validate_on_submit():
        meal = Meal(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(meal)
        db.session.commit()
        flash(f'Meal "{form.name.data}" created successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('meals'))

@app.route('/edit_meal/<int:meal_id>', methods=['GET', 'POST'])
@login_required
def edit_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if meal belongs to the current user
    if meal.user_id != current_user.id:
        flash('You are not authorized to edit this meal.', 'danger')
        return redirect(url_for('meals'))
    
    form = MealForm()
    
    if request.method == 'GET':
        form.name.data = meal.name
        form.description.data = meal.description
    
    if form.validate_on_submit():
        meal.name = form.name.data
        meal.description = form.description.data
        
        db.session.commit()
        flash(f'Meal "{meal.name}" updated successfully!', 'success')
        return redirect(url_for('meals'))
    
    return render_template('edit_meal.html', form=form, meal=meal)

@app.route('/delete_meal/<int:meal_id>', methods=['POST'])
@login_required
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if meal belongs to the current user
    if meal.user_id != current_user.id:
        flash('You are not authorized to delete this meal.', 'danger')
        return redirect(url_for('meals'))
    
    db.session.delete(meal)
    db.session.commit()
    flash(f'Meal "{meal.name}" deleted successfully!', 'success')
    return redirect(url_for('meals'))

@app.route('/add_meal_item/<int:meal_id>', methods=['POST'])
@login_required
def add_meal_item(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if meal belongs to the current user
    if meal.user_id != current_user.id:
        flash('You are not authorized to modify this meal.', 'danger')
        return redirect(url_for('meals'))
    
    form = MealItemForm()
    
    # Populate the food item choices for the form
    form.custom_item_id.choices = [
        (item.id, f"{item.name} ({item.quantity} {item.unit})")
        for item in CustomItem.query.filter_by(user_id=current_user.id).all()
    ]
    
    if form.validate_on_submit():
        # Check if the selected food item exists and belongs to the user
        food_item = CustomItem.query.get(form.custom_item_id.data)
        if not food_item or food_item.user_id != current_user.id:
            flash('Invalid food item selected.', 'danger')
            return redirect(url_for('meals'))
        
        meal_item = MealItem(
            meal_id=meal.id,
            custom_item_id=form.custom_item_id.data,
            quantity=form.quantity.data
        )
        
        db.session.add(meal_item)
        db.session.commit()
        flash(f'Added {food_item.name} to meal "{meal.name}"!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('meals'))

@app.route('/search_food_items')
@login_required
def search_food_items():
    """API endpoint to search for food items by name"""
    query = request.args.get('query', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    items = CustomItem.query.filter(
        CustomItem.user_id == current_user.id,
        CustomItem.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    results = []
    for item in items:
        results.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'unit': item.unit,
            'quantity': item.quantity,
            'calories': item.calories,
            'protein': item.protein,
            'display': f"{item.name} ({item.quantity} {item.unit}) - {item.calories} cal"
        })
    
    return jsonify(results)

@app.route('/delete_meal_item/<int:meal_item_id>', methods=['POST'])
@login_required
def delete_meal_item(meal_item_id):
    meal_item = MealItem.query.get_or_404(meal_item_id)
    meal = Meal.query.get(meal_item.meal_id)
    
    # Check if the meal belongs to the current user
    if meal.user_id != current_user.id:
        flash('You are not authorized to modify this meal.', 'danger')
        return redirect(url_for('meals'))
    
    food_item = CustomItem.query.get(meal_item.custom_item_id)
    db.session.delete(meal_item)
    db.session.commit()
    
    flash(f'Removed {food_item.name} from meal "{meal.name}"!', 'success')
    return redirect(url_for('meals'))

@app.route('/add_meal_to_log/<int:meal_id>', methods=['POST'])
@login_required
def add_meal_to_log(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if meal belongs to the current user
    if meal.user_id != current_user.id:
        flash('You are not authorized to use this meal.', 'danger')
        return redirect(url_for('meals'))
    
    # Create a food log entry for the entire meal
    food_log = FoodLog(
        user_id=current_user.id,
        name=meal.name,
        quantity=1,
        calories=round(meal.total_calories,2),
        protein=round(meal.total_protein),
        carbohydrates=round(meal.total_carbs,2),
        fiber=round(meal.total_fiber,2),
        sugar=round(meal.total_sugar,2),
        sodium=round(meal.total_sodium,2),
        description=f"Added meal: {meal.name}",
        meal_id=meal.id
    )
    
    db.session.add(food_log)
    db.session.commit()
    
    flash(f'Added meal "{meal.name}" with {meal.total_calories} calories to your food log!', 'success')
    return redirect(url_for('dashboard'))

# User profile route
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.weight.data = current_user.weight
        form.height.data = current_user.height
        form.age.data = current_user.age
        form.gender.data = current_user.gender
        form.activity_level.data = current_user.activity_level
        form.motive.data = current_user.motive
    
    if form.validate_on_submit():
        # Check if the username is being changed and is already taken
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('That username is already taken. Please choose another one.', 'danger')
            return redirect(url_for('profile'))
        
        # Check if the email is being changed and is already registered
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('That email is already registered. Please use a different one.', 'danger')
            return redirect(url_for('profile'))
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.weight = form.weight.data
        current_user.height = form.height.data
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.activity_level = form.activity_level.data
        current_user.motive = form.motive.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

# API routes for chart data
@app.route('/api/chart_data')
@login_required
def chart_data():
    # Get date range parameters
    period = request.args.get('period', 'week')
    
    today = datetime.now(tz_ist).date()
    
    if period == 'week':
        days = 7
        start_date = today - timedelta(days=days-1)
        date_format = '%a'  # Abbreviated weekday name
    elif period == 'month':
        days = 30
        start_date = today - timedelta(days=days-1)
        date_format = '%d'  # Day of month
    else:  # year
        # Group by month for a year
        months = 12
        start_date = (today - timedelta(days=365)).replace(day=1)
        date_format = '%b'  # Abbreviated month name
        
    # Initialize data structures
    if period == 'year':
        # For year, we group by month
        labels = [(today - timedelta(days=30*i)).strftime(date_format) for i in range(months-1, -1, -1)]
        food_data = [0] * months
        exercise_data = [0] * months
        
        # Get food logs for the past year
        food_logs = FoodLog.query.filter(
            FoodLog.user_id == current_user.id,
            FoodLog.date >= start_date
        ).all()
        
        # Get exercise logs for the past year
        exercise_logs = ExerciseLog.query.filter(
            ExerciseLog.user_id == current_user.id,
            ExerciseLog.date >= start_date
        ).all()
        
        # Aggregate data by month
        for log in food_logs:
            month_idx = months - 1 - ((today.year - log.date.year) * 12 + (today.month - log.date.month))
            if 0 <= month_idx < months:
                food_data[month_idx] += log.calories
        
        for log in exercise_logs:
            month_idx = months - 1 - ((today.year - log.date.year) * 12 + (today.month - log.date.month))
            if 0 <= month_idx < months:
                exercise_data[month_idx] += log.calories_burned
    else:
        # For week or month, we group by day
        labels = [(start_date + timedelta(days=i)).strftime(date_format) for i in range(days)]
        food_data = [0] * days
        exercise_data = [0] * days
        
        # Get food logs for the period
        food_logs = FoodLog.query.filter(
            FoodLog.user_id == current_user.id,
            FoodLog.only_date >= start_date,
            FoodLog.only_date <= today
        ).all()
        
        # Get exercise logs for the period
        exercise_logs = ExerciseLog.query.filter(
            ExerciseLog.user_id == current_user.id,
            ExerciseLog.only_date >= start_date,
            ExerciseLog.only_date <= today
        ).all()
        
        # Aggregate data by day
        for log in food_logs:
            day_idx = (log.date.date() - start_date).days
            if 0 <= day_idx < days:
                food_data[day_idx] += log.calories
        
        for log in exercise_logs:
            day_idx = (log.date.date() - start_date).days
            if 0 <= day_idx < days:
                exercise_data[day_idx] += log.calories_burned
    
    # Calculate net calories (intake - burned)
    net_data = [food_data[i] - exercise_data[i] for i in range(len(food_data))]
    
    return jsonify({
        'labels': labels,
        'foodData': food_data,
        'exerciseData': exercise_data,
        'netData': net_data
    })

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/daily')
@login_required
def daily_report():
    """
    Detailed daily report page showing nutrition and exercise data
    """
    # Get the requested date or default to today
    date_param = request.args.get('date')
    print(date_param)
    if date_param:
        try:
            view_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            view_date = date.today()
    else:
        view_date = date.today()
    print(view_date)
    
    # Calculate previous and next days for navigation
    prev_date = view_date - timedelta(days=1)
    next_date = view_date + timedelta(days=1)
    if next_date > date.today():
        next_date = None
    
    # Get user's calorie requirements and targets
    user_has_complete_profile = all([
        current_user.weight, 
        current_user.height, 
        current_user.age, 
        current_user.gender, 
        current_user.activity_level, 
        current_user.motive
    ])
    
    if user_has_complete_profile:
        from nutrition_calculator import get_full_recommendations
        recommendations = get_full_recommendations(current_user)
        target_calories = recommendations['nutrition']['calories']
        target_protein = recommendations['nutrition']['protein']
        target_carbs = recommendations['nutrition']['carbs']
        target_fiber = recommendations['nutrition']['fiber']
        target_sugar = recommendations['nutrition']['sugar']
        target_sodium = recommendations['nutrition']['sodium']
    else:
        # Default values if user hasn't completed their profile
        target_calories = 2000
        target_protein = 50
        target_carbs = 250
        target_fiber = 28
        target_sugar = 50
        target_sodium = 2300
    
    # Get all food logs for the specified date
    food_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.only_date == view_date
    ).order_by(FoodLog.date).all()
    
    # Get all exercise logs for the specified date
    exercise_logs = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date == view_date
    ).order_by(ExerciseLog.date).all()
    
    # Categorize food logs by meal type
    breakfast_logs = [log for log in food_logs if log.meal_type == 'breakfast']
    lunch_logs = [log for log in food_logs if log.meal_type == 'lunch']
    dinner_logs = [log for log in food_logs if log.meal_type == 'dinner']
    snack_logs = [log for log in food_logs if log.meal_type == 'snack']
    other_logs = [log for log in food_logs if log.meal_type not in ['breakfast', 'lunch', 'dinner', 'snack'] or log.meal_type is None]
    
    # Calculate nutrition totals
    total_calories = sum(log.calories for log in food_logs) if food_logs else 0
    total_protein = sum(log.protein for log in food_logs) if food_logs else 0
    total_carbs = sum(log.carbohydrates for log in food_logs) if food_logs else 0
    total_fiber = sum(log.fiber for log in food_logs) if food_logs else 0
    total_sugar = sum(log.sugar for log in food_logs) if food_logs else 0
    total_sodium = sum(log.sodium for log in food_logs) if food_logs else 0
    
    # Calculate exercise totals
    total_calories_burned = sum(log.calories_burned for log in exercise_logs) if exercise_logs else 0
    total_minutes = sum(log.duration for log in exercise_logs) if exercise_logs else 0
    
    # Calculate percentages of daily targets and determine status colors
    if target_calories > 0:
        calories_percent = round((total_calories / target_calories) * 100)
        calories_status = 'success' if calories_percent <= 105 else 'danger'
    else:
        calories_percent = 0
        calories_status = 'secondary'
        
    if target_protein > 0:
        protein_percent = round((total_protein / target_protein) * 100)
        protein_status = 'success' if protein_percent >= 90 else 'warning'
    else:
        protein_percent = 0
        protein_status = 'secondary'
        
    if target_carbs > 0:
        carbs_percent = round((total_carbs / target_carbs) * 100)
        carbs_status = 'success' if carbs_percent <= 110 else 'warning'
    else:
        carbs_percent = 0
        carbs_status = 'secondary'
        
    if target_fiber > 0:
        fiber_percent = round((total_fiber / target_fiber) * 100)
        fiber_status = 'success' if fiber_percent >= 90 else 'warning'
    else:
        fiber_percent = 0
        fiber_status = 'secondary'
    
    if target_sugar > 0:
        sugar_percent = round((total_sugar / target_sugar) * 100)
        sugar_status = 'success' if sugar_percent <= 100 else 'danger'
    else:
        sugar_percent = 0
        sugar_status = 'secondary'
        
    if target_sodium > 0:
        sodium_percent = round((total_sodium / target_sodium) * 100)
        sodium_status = 'success' if sodium_percent <= 100 else 'danger'
    else:
        sodium_percent = 0
        sodium_status = 'secondary'
    
    # Generate hourly calorie distribution for chart
    hourly_data = [0] * 24
    hourly_target = [target_calories / 24] * 24  # Distribute daily target evenly
    for log in food_logs:
        hour = log.date.hour
        hourly_data[hour] += log.calories
    
    return render_template(
        'daily_report.html',
        date=view_date,
        prev_date=prev_date,
        next_date=next_date,
        food_logs=food_logs,
        exercise_logs=exercise_logs,
        breakfast_logs=breakfast_logs,
        lunch_logs=lunch_logs,
        dinner_logs=dinner_logs,
        snack_logs=snack_logs,
        other_logs=other_logs,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fiber=total_fiber,
        total_sugar=total_sugar,
        total_sodium=total_sodium,
        total_calories_burned=total_calories_burned,
        total_minutes=total_minutes,
        net_calories=total_calories - total_calories_burned,
        target_calories=target_calories,
        target_protein=target_protein,
        target_carbs=target_carbs,
        target_fiber=target_fiber,
        target_sugar=target_sugar,
        target_sodium=target_sodium,
        calories_percent=calories_percent,
        calories_status=calories_status,
        protein_percent=protein_percent,
        protein_status=protein_status,
        carbs_percent=carbs_percent,
        carbs_status=carbs_status,
        fiber_percent=fiber_percent,
        fiber_status=fiber_status,
        sugar_percent=sugar_percent,
        sugar_status=sugar_status,
        sodium_percent=sodium_percent,
        sodium_status=sodium_status,
        hourly_data=json.dumps(hourly_data),
        hourly_target=json.dumps(hourly_target),
        has_complete_profile=user_has_complete_profile
    )

@app.route('/weekly')
@login_required
def weekly_report():
    """
    Detailed weekly report page showing nutrition and exercise data
    """
    # Get start date parameter (default to start of current week)
    date_str = request.args.get('start_date')
    today = datetime.now(tz_ist).date()
    
    if date_str:
        try:
            start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            # Default to start of current week (Monday)
            start_date = today - timedelta(days=today.weekday())
    else:
        # Default to start of current week (Monday)
        start_date = today - timedelta(days=today.weekday())
    
    # Calculate end date (start_date + 6 days = one week)
    end_date = start_date + timedelta(days=6)
    
    # Get previous and next week for navigation
    prev_week = start_date - timedelta(days=7)
    next_week = start_date + timedelta(days=7)
    
    # Don't allow future weeks
    if next_week > today:
        next_week = None
    
    # Get nutrition data for the selected week
    food_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.only_date >= start_date,
        FoodLog.only_date <= end_date
    ).order_by(FoodLog.date).all()
    
    # Get exercise data for the selected week
    exercise_logs = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date >= start_date,
        ExerciseLog.only_date <= end_date
    ).order_by(ExerciseLog.date).all()
    
    # Calculate totals for the week
    weekly_calories = sum(log.calories for log in food_logs)
    weekly_protein = sum(log.protein for log in food_logs)
    weekly_carbs = sum(log.carbohydrates for log in food_logs)
    weekly_fiber = sum(log.fiber for log in food_logs)
    weekly_sugar = sum(log.sugar for log in food_logs)
    weekly_sodium = sum(log.sodium for log in food_logs)
    
    weekly_exercise_minutes = sum(log.duration for log in exercise_logs)
    weekly_calories_burned = sum(log.calories_burned for log in exercise_logs)
    
    # Calculate net calories
    weekly_net_calories = weekly_calories - weekly_calories_burned
    
    # Calculate daily breakdown for the week
    days = []
    daily_calories = []
    daily_protein = []
    daily_carbs = []
    daily_exercise_minutes = []
    daily_calories_burned = []
    
    for i in range(7):
        day = start_date + timedelta(days=i)
        days.append(day.strftime('%a'))
        
        # Get food logs for this day
        day_food = [log for log in food_logs if log.date.date() == day]
        day_calories = sum(log.calories for log in day_food)
        day_protein = sum(log.protein for log in day_food)
        day_carbs = sum(log.carbohydrates for log in day_food)
        
        # Get exercise logs for this day
        day_exercise = [log for log in exercise_logs if log.date.date() == day]
        day_exercise_minutes = sum(log.duration for log in day_exercise)
        day_calories_burned = sum(log.calories_burned for log in day_exercise)
        
        daily_calories.append(day_calories)
        daily_protein.append(day_protein)
        daily_carbs.append(day_carbs)
        daily_exercise_minutes.append(day_exercise_minutes)
        daily_calories_burned.append(day_calories_burned)
    
    # Count total unique days with food logs
    days_with_food = len(set(log.date.date() for log in food_logs))
    
    # Count total unique days with exercise logs
    days_with_exercise = len(set(log.date.date() for log in exercise_logs))
    
    return render_template(
        'weekly_report.html',
        start_date=start_date,
        end_date=end_date,
        prev_week=prev_week,
        next_week=next_week,
        weekly_calories=weekly_calories,
        weekly_protein=weekly_protein,
        weekly_carbs=weekly_carbs,
        weekly_fiber=weekly_fiber,
        weekly_sugar=weekly_sugar,
        weekly_sodium=weekly_sodium,
        weekly_exercise_minutes=weekly_exercise_minutes,
        weekly_calories_burned=weekly_calories_burned,
        weekly_net_calories=weekly_net_calories,
        days=days,
        daily_calories=daily_calories,
        daily_protein=daily_protein,
        daily_carbs=daily_carbs,
        daily_exercise_minutes=daily_exercise_minutes,
        daily_calories_burned=daily_calories_burned,
        days_with_food=days_with_food,
        days_with_exercise=days_with_exercise,
        food_logs=food_logs,
        exercise_logs=exercise_logs,
        timedelta=timedelta
    )

@app.route('/monthly')
@login_required
def monthly_report():
    """
    Detailed monthly report page showing nutrition and exercise data
    """
    # Get month and year parameters (default to current month)
    month_str = request.args.get('month')
    year_str = request.args.get('year')
    today = datetime.now(tz_ist).date()
    
    if month_str and year_str:
        try:
            month = int(month_str)
            year = int(year_str)
            if month < 1 or month > 12:
                month = today.month
                year = today.year
        except ValueError:
            month = today.month
            year = today.year
    else:
        month = today.month
        year = today.year
    
    # Calculate start and end dates for the selected month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Calculate previous and next month for navigation
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Don't allow future months
    if (next_year > today.year) or (next_year == today.year and next_month > today.month):
        next_month = None
        next_year = None
    
    # Get nutrition data for the selected month
    food_logs = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.only_date >= start_date,
        FoodLog.only_date <= end_date
    ).order_by(FoodLog.date).all()
    
    # Get exercise data for the selected month
    exercise_logs = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date >= start_date,
        ExerciseLog.only_date <= end_date
    ).order_by(ExerciseLog.date).all()
    
    # Calculate totals for the month
    monthly_calories = sum(log.calories for log in food_logs)
    monthly_protein = sum(log.protein for log in food_logs)
    monthly_carbs = sum(log.carbohydrates for log in food_logs)
    monthly_fiber = sum(log.fiber for log in food_logs)
    monthly_sugar = sum(log.sugar for log in food_logs)
    monthly_sodium = sum(log.sodium for log in food_logs)
    
    monthly_exercise_minutes = sum(log.duration for log in exercise_logs)
    monthly_calories_burned = sum(log.calories_burned for log in exercise_logs)
    
    # Calculate net calories
    monthly_net_calories = monthly_calories - monthly_calories_burned
    
    # Calculate daily breakdown for charting
    days_in_month = (end_date - start_date).days + 1
    dates = []
    daily_calories = []
    daily_calories_burned = []
    
    for i in range(days_in_month):
        day = start_date + timedelta(days=i)
        dates.append(day.day)  # Just the day number
        
        # Get food logs for this day
        day_food = [log for log in food_logs if log.date.date() == day]
        day_calories = sum(log.calories for log in day_food)
        
        # Get exercise logs for this day
        day_exercise = [log for log in exercise_logs if log.date.date() == day]
        day_calories_burned = sum(log.calories_burned for log in day_exercise)
        
        daily_calories.append(day_calories)
        daily_calories_burned.append(day_calories_burned)
    
    # Calculate weekly breakdown
    weeks = []
    weekly_breakdown = []
    current_week = []
    current_week_total = 0
    
    # Fill in days from previous month to start week on Monday
    first_day_weekday = start_date.weekday()
    if first_day_weekday > 0:
        weeks.append("Week 1 (Partial)")
    else:
        weeks.append("Week 1")
    
    for i in range(days_in_month):
        day = start_date + timedelta(days=i)
        day_weekday = day.weekday()
        
        # Get food logs for this day
        day_food = [log for log in food_logs if log.date.date() == day]
        day_calories = sum(log.calories for log in day_food)
        
        if day_weekday == 0 and i > 0:  # Monday, start new week
            weekly_breakdown.append(current_week_total)
            current_week = []
            current_week_total = 0
            week_num = len(weekly_breakdown) + 1
            if i + 7 > days_in_month:
                weeks.append(f"Week {week_num} (Partial)")
            else:
                weeks.append(f"Week {week_num}")
        
        current_week_total += day_calories
    
    # Add the last week
    weekly_breakdown.append(current_week_total)
    
    # Count days with logs
    days_with_food = len(set(log.date.date() for log in food_logs))
    days_with_exercise = len(set(log.date.date() for log in exercise_logs))
    
    # Calculate daily averages (only for days with data)
    avg_daily_calories = monthly_calories / days_with_food if days_with_food > 0 else 0
    avg_daily_protein = monthly_protein / days_with_food if days_with_food > 0 else 0
    avg_daily_carbs = monthly_carbs / days_with_food if days_with_food > 0 else 0
    avg_daily_exercise = monthly_exercise_minutes / days_with_exercise if days_with_exercise > 0 else 0
    
    return render_template(
        'monthly_report.html',
        month=month,
        year=year,
        month_name=date(year, month, 1).strftime('%B'),
        start_date=start_date,
        end_date=end_date,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        monthly_calories=monthly_calories,
        monthly_protein=monthly_protein,
        monthly_carbs=monthly_carbs,
        monthly_fiber=monthly_fiber,
        monthly_sugar=monthly_sugar,
        monthly_sodium=monthly_sodium,
        monthly_exercise_minutes=monthly_exercise_minutes,
        monthly_calories_burned=monthly_calories_burned,
        monthly_net_calories=monthly_net_calories,
        days_with_food=days_with_food,
        days_with_exercise=days_with_exercise,
        avg_daily_calories=avg_daily_calories,
        avg_daily_protein=avg_daily_protein,
        avg_daily_carbs=avg_daily_carbs,
        avg_daily_exercise=avg_daily_exercise,
        dates=dates,
        daily_calories=daily_calories,
        daily_calories_burned=daily_calories_burned,
        weeks=weeks,
        weekly_breakdown=weekly_breakdown,
        food_logs=food_logs,
        exercise_logs=exercise_logs,
        timedelta=timedelta,
        date=date
    )

@app.route('/compare')
@login_required
def compare():
    """
    Page to compare ideal vs. actual nutrition and exercise
    """
    # Import nutrition calculator
    from nutrition_calculator import get_full_recommendations
    
    # Check if user has enough profile data
    if not all([current_user.weight, current_user.height, current_user.age, 
                current_user.gender, current_user.activity_level, current_user.motive]):
        flash('Please complete your profile first to get personalized recommendations.', 'warning')
        return redirect(url_for('profile'))
    
    # Get recommendations
    recommendations = get_full_recommendations(current_user)
    
    # Calculate today's nutrition summary
    today = datetime.now(tz_ist).date()
    todays_food = FoodLog.query.filter(
        FoodLog.user_id == current_user.id,
        FoodLog.only_date == today
    ).all()
    
    today_calories = sum(log.calories for log in todays_food)
    today_protein = sum(log.protein for log in todays_food)
    today_carbs = sum(log.carbohydrates for log in todays_food)
    today_fiber = sum(log.fiber for log in todays_food)
    today_sugar = sum(log.sugar for log in todays_food)
    today_sodium = sum(log.sodium for log in todays_food)
    
    # Calculate today's exercise summary
    todays_exercise = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date == today
    ).all()
    
    today_exercise_minutes = sum(log.duration for log in todays_exercise)
    today_calories_burned = sum(log.calories_burned for log in todays_exercise)
    
    # Calculate past week's exercise data
    week_ago = today - timedelta(days=7)
    
    weekly_exercise = ExerciseLog.query.filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.only_date >= week_ago,
        ExerciseLog.only_date <= today
    ).all()
    
    weekly_exercise_minutes = sum(log.duration for log in weekly_exercise)
    weekly_calories_burned = sum(log.calories_burned for log in weekly_exercise)
    
    # Count unique days with strength training in the past week
    strength_training_days = set()
    for log in weekly_exercise:
        # Simple heuristic: workouts with less than 20 minutes and burning
        # fewer than 100 calories are likely strength training
        if (log.duration < 20 and log.calories_burned < 100) or "strength" in log.name.lower() or "weight" in log.name.lower():
            strength_training_days.add(log.date.date())
    
    return render_template(
        'compare.html',
        recommendations=recommendations,
        today_nutrition={
            'calories': round(today_calories,2),
            'protein': round(today_protein,2),
            'carbs': round(today_carbs,2),
            'fiber': round(today_fiber,2),
            'sugar': round(today_sugar,2),
            'sodium': round(today_sodium,2)
        },
        today_exercise={
            'minutes': today_exercise_minutes,
            'calories_burned': round(today_calories_burned,2),
        },
        weekly_exercise={
            'minutes': weekly_exercise_minutes,
            'calories_burned': round(weekly_calories_burned,2),
            'strength_days': len(strength_training_days)
        }
    )

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
