'''
Nutrition Calculator for HealthTracker App
Calculates recommended nutrition and exercise based on user attributes and goals
'''

def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: 'male', 'female', or 'other'
    
    Returns:
        BMR value in calories
    """
    if gender.lower() == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender.lower() == 'female':
        return (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        # Non-binary: average of male and female offsets
        return (10 * weight) + (6.25 * height) - (5 * age) - 78


def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on BMR and activity level
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: one of 'sedentary', 'light', 'moderate', 'active', 'very_active'

    Returns:
        TDEE value in calories
    """
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return bmr * multipliers.get(activity_level, 1.2)


def calculate_target_calories(tdee, motive, weight):
    """
    Determine daily calorie goal based on user motive.

    Args:
        tdee: Total Daily Energy Expenditure
        motive: 'lose', 'maintain', or 'gain'
        weight: Weight in kg

    Returns:
        target_calories (float)
    """
    factors = {
        'lose': 0.8,      # 20% deficit
        'maintain': 1.0,  # maintain
        'gain': 1.15      # 15% surplus
    }
    return tdee * factors.get(motive, 1.0)


def calculate_target_macros(target_calories, motive, weight):
    """
    Calculate macronutrient targets based on calorie goal and weight-based protein needs.

    Args:
        target_calories: Daily calorie goal
        motive: 'lose', 'maintain', or 'gain'
        weight: Weight in kg

    Returns:
        Dict of macro targets (calories, protein_g, fat_g, carbs_g, fiber_g, sugar_g, sodium_mg)
    """
    # Protein guidelines (g per kg)
    protein_per_kg = {
        'lose': 1.8,      # preserve muscle during weight loss
        'maintain': 1.2,  # general maintenance
        'gain': 1.6       # support muscle gain
    }
    # Calculate protein
    p_factor = protein_per_kg.get(motive, 1.2)
    protein_g = weight * p_factor
    protein_cal = protein_g * 4  # 4 kcal per gram

    # Fat set at 25% of calories
    fat_pct = 0.25
    fat_cal = target_calories * fat_pct
    fat_g = fat_cal / 9          # 9 kcal per gram

    # Carbs fill remaining calories
    remaining_cal = target_calories - (protein_cal + fat_cal)
    carbs_cal = max(remaining_cal, 0)
    carbs_g = carbs_cal / 4       # 4 kcal per gram

    # Fiber and sugar guidelines
    fiber_g = (target_calories / 1000) * 14   # 14g per 1000 kcal
    sugar_g = (target_calories * 0.10) / 4    # max 10% calories from sugar

    # Sodium upper limit
    sodium_mg = 2300

    return {
        'calories': round(target_calories),
        'protein': round(protein_g),
        'carbs': round(carbs_g),
        'fat': round(fat_g),
        'fiber': round(fiber_g),
        'sugar': round(sugar_g),
        'sodium': sodium_mg
    }


def calculate_exercise_recommendations(weight, motive, activity_level):
    """
    Calculate recommended exercise based on weight, goal, and activity level.

    Args:
        weight: Weight in kg
        motive: 'lose', 'maintain', or 'gain'
        activity_level: one of 'sedentary', 'light', 'moderate', 'active', 'very_active'

    Returns:
        Dict of exercise recommendations
    """
    # Base weekly exercise minutes
    base_minutes = {
        'sedentary': 150,
        'light': 180,
        'moderate': 210,
        'active': 240,
        'very_active': 300
    }.get(activity_level, 150)

    # Adjust for motive
    if motive == 'lose':
        cardio_minutes = base_minutes * 1.2
        strength_days = 2
    elif motive == 'gain':
        cardio_minutes = base_minutes * 0.8
        strength_days = 4
    else:  # maintain
        cardio_minutes = base_minutes
        strength_days = 3

    # Estimate calories burned (MET=7)
    cal_per_min = 0.0175 * 7 * weight
    weekly_cal_burn = cardio_minutes * cal_per_min

    return {
        'weekly_cardio_minutes': round(cardio_minutes),
        'weekly_strength_days': strength_days,
        'daily_cardio_minutes': round(cardio_minutes / 7),
        'weekly_calories_burned': round(weekly_cal_burn),
        'daily_calories_burned': round(weekly_cal_burn / 7)
    }


def get_full_recommendations(user):
    """
    Generate comprehensive nutrition and exercise recommendations.

    Args:
        user: Object with attributes weight (kg), height (cm), age (years), gender, activity_level, motive

    Returns:
        Dict with BMR, TDEE, nutrition, and exercise recommendations
    """
    bmr = calculate_bmr(user.weight, user.height, user.age, user.gender)
    tdee = calculate_tdee(bmr, user.activity_level)
    target_cal = calculate_target_calories(tdee, user.motive, user.weight)
    nutrition = calculate_target_macros(target_cal, user.motive, user.weight)
    exercise = calculate_exercise_recommendations(user.weight, user.motive, user.activity_level)

    return {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'nutrition': nutrition,
        'exercise': exercise
    }
