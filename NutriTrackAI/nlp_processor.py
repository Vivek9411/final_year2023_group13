# import re
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from models import CustomItem
# from app import db
#
# # Download required NLTK data
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')
#
# try:
#     nltk.data.find('corpora/stopwords')
# except LookupError:
#     nltk.download('stopwords')
#
# class NLPProcessor:
#     def __init__(self):
#         self.stop_words = set(stopwords.words('english'))
#         self.food_quantity_patterns = [
#             r'(\d+(?:\.\d+)?)\s*(cup|cups|g|grams|kg|kilograms|lb|lbs|pounds|oz|ounce|ounces|ml|l|liter|liters|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|slice|slices|piece|pieces)',
#             r'(\d+(?:\.\d+)?)',  # Just numbers
#         ]
#         self.activity_patterns = [
#             r'(ran|running|jogging|jogged|walked|walking|cycling|cycled|swimming|swam|yoga|hiit|workout|exercised|training|trained)',
#             r'(\d+(?:\.\d+)?)\s*(minutes|mins|min|hours|hour|hr|hrs)',
#         ]
#
#         # Common food database with nutrition info per standard unit
#         self.food_database = {
#             'apple': {'calories': 95, 'protein': 0.5, 'carbohydrates': 25, 'fiber': 4, 'sugar': 19, 'sodium': 2, 'unit': 'piece', 'quantity': 1},
#             'banana': {'calories': 105, 'protein': 1.3, 'carbohydrates': 27, 'fiber': 3.1, 'sugar': 14, 'sodium': 1, 'unit': 'piece', 'quantity': 1},
#             'orange': {'calories': 62, 'protein': 1.2, 'carbohydrates': 15.4, 'fiber': 3.1, 'sugar': 12, 'sodium': 0, 'unit': 'piece', 'quantity': 1},
#             'bread': {'calories': 264, 'protein': 9, 'carbohydrates': 49, 'fiber': 3, 'sugar': 6, 'sodium': 491, 'unit': 'slice', 'quantity': 1},
#             'rice': {'calories': 130, 'protein': 2.7, 'carbohydrates': 28, 'fiber': 0.6, 'sugar': 0.1, 'sodium': 1, 'unit': 'cup', 'quantity': 1},
#             'pasta': {'calories': 221, 'protein': 8.1, 'carbohydrates': 43.2, 'fiber': 2.5, 'sugar': 0.8, 'sodium': 1, 'unit': 'cup', 'quantity': 1},
#             'chicken': {'calories': 165, 'protein': 31, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 74, 'unit': 'piece', 'quantity': 1}, # 100g
#             'beef': {'calories': 250, 'protein': 26, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 72, 'unit': 'piece', 'quantity': 1}, # 100g
#             'milk': {'calories': 149, 'protein': 8, 'carbohydrates': 12, 'fiber': 0, 'sugar': 12, 'sodium': 105, 'unit': 'cup', 'quantity': 1},
#             'egg': {'calories': 72, 'protein': 6.3, 'carbohydrates': 0.4, 'fiber': 0, 'sugar': 0.2, 'sodium': 71, 'unit': 'piece', 'quantity': 1},
#         }
#
#         # Common exercises with calories burned per minute (based on 70kg person)
#         self.exercise_database = {
#             'running': 10.0,  # 10 calories per minute
#             'jogging': 8.0,
#             'walking': 4.0,
#             'cycling': 7.0,
#             'swimming': 8.0,
#             'yoga': 3.0,
#             'hiit': 12.0,
#             'workout': 8.0,
#             'training': 7.0,
#         }
#
#     def process_food_query(self, query, user_id):
#         """Process natural language food query and extract nutrition information"""
#         query = query.lower()
#         tokens = word_tokenize(query)
#         tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
#
#         # Extract quantities
#         quantity = 1.0
#         unit = "serving"
#         food_item = None
#
#         # Try to find quantities and units
#         for pattern in self.food_quantity_patterns:
#             matches = re.findall(pattern, query)
#             if matches:
#                 if isinstance(matches[0], tuple):
#                     quantity = float(matches[0][0])
#                     if len(matches[0]) > 1:
#                         unit = matches[0][1]
#                 else:
#                     quantity = float(matches[0])
#                 break
#
#         # Try to find food item
#         for token in tokens:
#             if token in self.food_database:
#                 food_item = token
#                 break
#
#         # If not found in basic database, check user's custom items
#         if not food_item:
#             custom_items = CustomItem.query.filter_by(user_id=user_id).all()
#             for item in custom_items:
#                 if item.name.lower() in query:
#                     food_item = item.name.lower()
#                     nutrition_data = {
#                         'calories': item.calories,
#                         'protein': item.protein,
#                         'carbohydrates': item.carbohydrates,
#                         'fiber': item.fiber,
#                         'sugar': item.sugar,
#                         'sodium': item.sodium,
#                         'unit': item.unit,
#                         'quantity': item.quantity
#                     }
#                     result = self._calculate_nutrition(nutrition_data, quantity, item.quantity)
#                     result['name'] = item.name
#                     result['value'] = quantity
#                     result['quantity'] = quantity
#                     result['result'] = True
#                     return result
#
#         # Calculate nutrition based on the found food item
#         if food_item:
#             nutrition_data = self.food_database[food_item]
#             result = self._calculate_nutrition(nutrition_data, quantity, nutrition_data['quantity'])
#             result['name'] = food_item
#             result['value'] = quantity
#             result['quantity'] = quantity
#             result['result'] = True
#             return result
#
#         # If no match found
#         return {
#             'result': False,
#             'message': "Food item not recognized. Please try again or add a custom food item."
#         }
#
#     def process_exercise_query(self, query):
#         """Process natural language exercise query and extract calories burned"""
#         query = query.lower()
#
#         # Extract exercise type
#         exercise_type = None
#         for pattern in self.activity_patterns:
#             matches = re.findall(pattern, query)
#             if matches and pattern.startswith('(ran|'):
#                 exercise_type = matches[0]
#                 if isinstance(exercise_type, tuple):
#                     exercise_type = exercise_type[0]
#                 break
#
#         # Extract duration
#         duration = 30  # Default duration in minutes
#         for pattern in self.activity_patterns:
#             matches = re.findall(pattern, query)
#             if matches and pattern.startswith('(\\d+'):
#                 if isinstance(matches[0], tuple):
#                     duration_val = float(matches[0][0])
#                     unit = matches[0][1] if len(matches[0]) > 1 else 'minutes'
#                     if 'hour' in unit:
#                         duration = duration_val * 60
#                     else:
#                         duration = duration_val
#                     break
#                 else:
#                     duration = float(matches[0])
#                     break
#
#         # Calculate calories burned
#         if exercise_type:
#             # Normalize the exercise type to match our database
#             normalized_type = None
#             for key in self.exercise_database:
#                 if key in exercise_type or exercise_type in key:
#                     normalized_type = key
#                     break
#
#             if normalized_type:
#                 calories_per_minute = self.exercise_database[normalized_type]
#                 calories_burned = calories_per_minute * duration
#
#                 return {
#                     'result': True,
#                     'name': normalized_type,
#                     'duration': duration,
#                     'calories_burned': round(calories_burned),
#                     'message': f"Burned approximately {round(calories_burned)} calories from {duration} minutes of {normalized_type}"
#                 }
#
#         return {
#             'result': False,
#             'message': "Exercise not recognized or duration not specified. Please try again."
#         }
#
#     def _calculate_nutrition(self, nutrition_data, quantity, base_quantity):
#         """Calculate nutrition values based on quantity"""
#         ratio = quantity / base_quantity
#         return {
#             'calories': int(nutrition_data['calories'] * ratio),
#             'protein': int(nutrition_data['protein'] * ratio),
#             'carbohydrates': int(nutrition_data['carbohydrates'] * ratio),
#             'fiber': int(nutrition_data['fiber'] * ratio),
#             'sugar': int(nutrition_data['sugar'] * ratio),
#             'sodium': int(nutrition_data['sodium'] * ratio),
#         }
#
#
#
# import requests
# import datetime
# import pytz
# API_ID = "127b9e9d"
# API_KEY = "d3f14705514a09f28cf0669fc0315c99"
# url = "https://trackapi.nutritionix.com/v2/natural/exercise"
# headers = {
#         "x-app-id": API_ID,
#         "x-app-key": API_KEY
#     }
# def findx(user_input, gender, weight, height, age, headers=headers):
#     tz_ist = pytz.timezone('Asia/Kolkata')
#     now_ist = datetime.datetime.now(tz_ist)
#     date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")
#     query = {
#      "query": user_input,
#      "gender": gender,
#      "weight_kg": weight,
#      "height_cm": height,
#      "age": age
#     }
#     response = requests.post(url=url, json=query, headers=headers)
#     print(response.raise_for_status())
#     print(response.json())
#     data = response.json()['exercises']
#     print(data)
#     new=[]
#     for each_exercise in data:
#         exercise = {
#             'exercise': each_exercise['user_input'],
#             'duration': each_exercise['duration_min'],
#             'calories': each_exercise['nf_calories'],
#             'date': date,
#             'time': time,
#             'description': user_input,
#         }
#         new.append(exercise)
#     # print(new)
#     return  new
#
#
# api_food = '3db00a91'
# api_key_food = '8dc67612535c89a55858b8ab37364320'
#
# url_food  ='http://127.0.0.1:5001/process_text'
# # headers_food = {
# #     "x-app-id": api_food,
# #     "x-app-key": api_key_food
# # }
# def find_food(user_input):
#     tz_ist = pytz.timezone('Asia/Kolkata')
#     now_ist = datetime.datetime.now(tz_ist)
#     date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")
#     query = {
#         "text": user_input,
#     }
#     response = requests.post(url=url_food, json=query)
#     print(response.text)
#
#     data = response.json().get('found', {})
#     missing = response.json().get('missing', [])
#     # print(data, missing, 'what and ahy')
#     food = []
#     for food_name in data.keys():
#         each_food = data[food_name]
#         # print(each_food)
#         # print(type(each_food))
#         foods ={
#             'food': food_name,
#             'date': date,
#             'time': time,
#             'serving_unit': each_food['value'],
#             'description': user_input,
#             'calories': each_food['calories'],
#             'protein': each_food['protein'],
#             'carbohydrates': each_food['carbohydrates'],
#             'sugar': each_food['sugar'],
#             'sodium': each_food['sodium'],
#             'quantity': each_food['quantity'],
#             'fiber': each_food['fiber'],
#         }
#         # print(each_food)
#         food.append(foods)
#     return food,missing
#

#
#
# print(find_food('eat 2 apple'))

import requests
import datetime
import pytz


class NLPProcessor:
    def __init__(self):
        self.nutritionix_config = {
            "exercise": {
                "url": "https://trackapi.nutritionix.com/v2/natural/exercise",
                "headers": {
                    "x-app-id": "127b9e9d",
                    "x-app-key": "d3f14705514a09f28cf0669fc0315c99"
                }
            },
            "food": {
                "url": "http://192.168.10.171:5001/process_text",
                "headers": {
                    "x-app-id": "3db00a91",
                    "x-app-key": "8dc67612535c89a55858b8ab37364320"
                }
            }
        }

    def process_exercise_query(self, user_input, gender, weight, height, age):
        """Process exercise query directly through Nutritionix API"""
        try:
            tz_ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.datetime.now(tz_ist)
            date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")

            response = requests.post(
                url=self.nutritionix_config['exercise']['url'],
                json={
                    "query": user_input,
                    "gender": gender,
                    "weight_kg": weight,
                    "height_cm": height,
                    "age": age
                },
                headers=self.nutritionix_config['exercise']['headers']
            )
            response.raise_for_status()

            exercises = []
            for each_exercise in response.json().get('exercises', []):
                exercises.append({
                    'exercise': each_exercise.get('user_input', ''),
                    'duration': each_exercise.get('duration_min', 0),
                    'calories': each_exercise.get('nf_calories', 0),
                    'date': date,
                    'time': time,
                    'description': user_input,
                })

            return exercises

        except Exception as e:
            print(f"Exercise API Error: {str(e)}")
            return []

    def process_food_query(self, user_input, user_id):
        """Process food query directly through API"""
        try:
            tz_ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.datetime.now(tz_ist)
            date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")

            response = requests.post(
                url=self.nutritionix_config['food']['url'],
                json={"text": user_input}
            )
            response.raise_for_status()
            # print(response.json())
            data = response.json().get('found', {})
            # print(data)
            missing = response.json().get('missing', {})
            print(missing)
            food_items = []

            for food_name, details in data.items():
                print(food_name, details)
                food_items.append({
                    'food': food_name,
                    'date': date,
                    'time': time,
                    'serving_unit': details.get('quantity', ''),
                    'description': user_input,
                    'calories': details.get('calories', 0),
                    'protein': details.get('protein', 0),
                    'carbohydrates': details.get('carbohydrates', 0),
                    'sugar': details.get('sugar', 0),
                    'sodium': details.get('sodium', 0),
                    'quantity': details.get('value', 1),
                    'fiber': details.get('fiber', 0),
                })
            # print(food_items)
            return food_items,missing

        except Exception as e:
            print(f"Food API Error: {str(e)}")
            return [], []