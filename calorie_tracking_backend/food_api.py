# import spacy

# # texts = [
# # 	'john goes for a walk in Berlin',
# # 	'mike is going to the store', 
# # 	'Elon Musk is the CEO at twitter', 
# # 	'Florian Dedov is the guy behind NeuralNine',
# # 	'what is the price of 4 bananas', 
# # 	'i ate 2 apples',
# # 	'i drink 50 ml milk'
# # ]

# # nlp = spacy.load('en_core_web_md')

# # # new_labels = nlp.get_pipe('ner').labels
# # # print(new_labels)


# # categories =['ORG', 'PERSON', 'LOC']

# # docs = [nlp(text) for text in texts]

# # for doc in docs:
# # 	entities = []

# # 	for ent  in doc.ents:
# # 		# if ent.label_ in categories:
# # 		entities.append((ent.text, ent.label_))

# # 	print(entities)

# import spacy
# import random

# from spacy.util import minibatch
# from spacy.training.example import Example
# from thinc.api import Adam

# train_data = [
#     (
#         "I ate 5 oranges and 3 apples",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "5"
#                 (8, 15, "PRODUCT"),      # "oranges"
#                 (20, 21, "QUANTITY"),    # "3"
#                 (22, 28, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "She ate 8 bananas and 6 pears",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "8"
#                 (10, 17, "PRODUCT"),     # "bananas"
#                 (22, 23, "QUANTITY"),    # "6"
#                 (24, 29, "PRODUCT")      # "pears"
#             ]
#         }
#     ),
#     (
#         "They ate 12 mangoes and 7 peaches",
#         {
#             'entities': [
#                 (9, 11, "QUANTITY"),     # "12"
#                 (12, 19, "PRODUCT"),     # "mangoes"
#                 (24, 25, "QUANTITY"),    # "7"
#                 (26, 33, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "I ate 2 strawberries and 5 plums",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "2"
#                 (8, 19, "PRODUCT"),      # "strawberries"
#                 (24, 25, "QUANTITY"),    # "5"
#                 (26, 31, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "We had 4 pears and 10 bananas",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "4"
#                 (9, 14, "PRODUCT"),      # "pears"
#                 (19, 21, "QUANTITY"),    # "10"
#                 (22, 29, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "She ate 9 apples and 2 plums",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "9"
#                 (10, 15, "PRODUCT"),     # "apples"
#                 (20, 21, "QUANTITY"),    # "2"
#                 (22, 27, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "I ate 11 grapes and 4 apricots",
#         {
#             'entities': [
#                 (6, 8, "QUANTITY"),      # "11"
#                 (9, 15, "PRODUCT"),      # "grapes"
#                 (20, 21, "QUANTITY"),    # "4"
#                 (22, 30, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "They had 15 cherries and 8 oranges",
#         {
#             'entities': [
#                 (9, 11, "QUANTITY"),     # "15"
#                 (12, 20, "PRODUCT"),     # "cherries"
#                 (25, 26, "QUANTITY"),    # "8"
#                 (27, 34, "PRODUCT")      # "oranges"
#             ]
#         }
#     ),
#     (
#         "We ate 6 watermelons and 3 pineapples",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "6"
#                 (9, 20, "PRODUCT"),      # "watermelons"
#                 (25, 26, "QUANTITY"),    # "3"
#                 (27, 37, "PRODUCT")      # "pineapples"
#             ]
#         }
#     ),
#     (
#         "He had 10 plums and 5 apples",
#         {
#             'entities': [
#                 (7, 9, "QUANTITY"),      # "10"
#                 (10, 15, "PRODUCT"),     # "plums"
#                 (20, 21, "QUANTITY"),    # "5"
#                 (22, 28, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "I ate 7 strawberries and 9 bananas",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "7"
#                 (8, 19, "PRODUCT"),      # "strawberries"
#                 (24, 25, "QUANTITY"),    # "9"
#                 (26, 33, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "She ate 6 peaches and 2 mangoes",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "6"
#                 (10, 17, "PRODUCT"),     # "peaches"
#                 (22, 23, "QUANTITY"),    # "2"
#                 (24, 31, "PRODUCT")      # "mangoes"
#             ]
#         }
#     ),
#     (
#         "They ate 3 apples and 5 plums",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "3"
#                 (11, 16, "PRODUCT"),     # "apples"
#                 (21, 22, "QUANTITY"),    # "5"
#                 (23, 28, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "I ate 4 mangoes and 6 apricots",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "4"
#                 (8, 15, "PRODUCT"),      # "mangoes"
#                 (20, 21, "QUANTITY"),    # "6"
#                 (22, 30, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "We had 5 cherries and 10 peaches",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "5"
#                 (9, 17, "PRODUCT"),      # "cherries"
#                 (22, 24, "QUANTITY"),    # "10"
#                 (25, 32, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "She ate 7 oranges and 3 watermelons",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "7"
#                 (10, 17, "PRODUCT"),     # "oranges"
#                 (22, 23, "QUANTITY"),    # "3"
#                 (24, 36, "PRODUCT")      # "watermelons"
#             ]
#         }
#     ),
#     (
#         "They had 8 apricots and 4 bananas",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "8"
#                 (11, 19, "PRODUCT"),     # "apricots"
#                 (24, 25, "QUANTITY"),    # "4"
#                 (26, 33, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "I ate 9 mangoes and 6 strawberries",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "9"
#                 (8, 15, "PRODUCT"),      # "mangoes"
#                 (20, 21, "QUANTITY"),    # "6"
#                 (22, 33, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "He had 5 peaches and 7 plums",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "5"
#                 (9, 16, "PRODUCT"),      # "peaches"
#                 (21, 22, "QUANTITY"),    # "7"
#                 (23, 28, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "We ate 10 apples and 6 grapes",
#         {
#             'entities': [
#                 (7, 9, "QUANTITY"),      # "10"
#                 (10, 15, "PRODUCT"),     # "apples"
#                 (20, 21, "QUANTITY"),    # "6"
#                 (22, 28, "PRODUCT")      # "grapes"
#             ]
#         }
#     ),
#     (
#         "She ate 6 strawberries and 8 plums",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "6"
#                 (10, 21, "PRODUCT"),     # "strawberries"
#                 (26, 27, "QUANTITY"),    # "8"
#                 (28, 33, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "I ate 2 pineapples and 5 oranges",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "2"
#                 (8, 18, "PRODUCT"),      # "pineapples"
#                 (23, 24, "QUANTITY"),    # "5"
#                 (25, 32, "PRODUCT")      # "oranges"
#             ]
#         }
#     ),
#     (
#         "They ate 3 grapes and 4 apricots",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "3"
#                 (11, 16, "PRODUCT"),     # "grapes"
#                 (21, 22, "QUANTITY"),    # "4"
#                 (23, 31, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "I had 5 apples and 7 mangoes",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "5"
#                 (8, 13, "PRODUCT"),      # "apples"
#                 (18, 19, "QUANTITY"),    # "7"
#                 (20, 27, "PRODUCT")      # "mangoes"
#             ]
#         }
#     ),
#     (
#         "She ate 6 pears and 8 strawberries",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "6"
#                 (10, 15, "PRODUCT"),     # "pears"
#                 (20, 21, "QUANTITY"),    # "8"
#                 (22, 33, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "They had 2 bananas and 6 peaches",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "2"
#                 (11, 18, "PRODUCT"),     # "bananas"
#                 (23, 24, "QUANTITY"),    # "6"
#                 (25, 32, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "I ate 3 mangoes and 7 apricots",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "3"
#                 (8, 15, "PRODUCT"),      # "mangoes"
#                 (20, 21, "QUANTITY"),    # "7"
#                 (22, 30, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "We ate 9 strawberries and 4 cherries",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "9"
#                 (9, 20, "PRODUCT"),      # "strawberries"
#                 (25, 26, "QUANTITY"),    # "4"
#                 (27, 35, "PRODUCT")      # "cherries"
#             ]
#         }
#     ),
#     (
#         "He ate 10 plums and 3 watermelons",
#         {
#             'entities': [
#                 (7, 9, "QUANTITY"),      # "10"
#                 (10, 15, "PRODUCT"),     # "plums"
#                 (20, 21, "QUANTITY"),    # "3"
#                 (22, 34, "PRODUCT")      # "watermelons"
#             ]
#         }
#     ),
#     (
#         "I ate 5 cherries and 6 peaches",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "5"
#                 (8, 16, "PRODUCT"),      # "cherries"
#                 (21, 22, "QUANTITY"),    # "6"
#                 (23, 30, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "We ate 8 bananas and 3 apples",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "8"
#                 (9, 16, "PRODUCT"),      # "bananas"
#                 (21, 22, "QUANTITY"),    # "3"
#                 (23, 29, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "They had 12 grapes and 6 apricots",
#         {
#             'entities': [
#                 (9, 11, "QUANTITY"),     # "12"
#                 (12, 17, "PRODUCT"),     # "grapes"
#                 (22, 23, "QUANTITY"),    # "6"
#                 (24, 32, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "I ate 2 bananas and 5 strawberries",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "2"
#                 (8, 15, "PRODUCT"),      # "bananas"
#                 (20, 21, "QUANTITY"),    # "5"
#                 (22, 33, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "She ate 8 oranges and 4 plums",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "8"
#                 (10, 17, "PRODUCT"),     # "oranges"
#                 (22, 23, "QUANTITY"),    # "4"
#                 (24, 29, "PRODUCT")      # "plums"
#             ]
#         }
#     ),
#     (
#         "He had 3 apricots and 9 peaches",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 17, "PRODUCT"),      # "apricots"
#                 (22, 23, "QUANTITY"),    # "9"
#                 (24, 31, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "They ate 4 watermelons and 10 strawberries",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "4"
#                 (11, 22, "PRODUCT"),     # "watermelons"
#                 (27, 29, "QUANTITY"),    # "10"
#                 (30, 41, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "I ate 7 grapes and 3 bananas",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "7"
#                 (8, 13, "PRODUCT"),      # "grapes"
#                 (18, 19, "QUANTITY"),    # "3"
#                 (20, 27, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "I ate 2 bananas with 100ml milk",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "2"
#                 (8, 15, "PRODUCT"),      # "bananas"
#                 (21, 26, "QUANTITY"),    # "100ml"
#                 (27, 31, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "She had 3 oranges and 200g apples",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "3"
#                 (10, 17, "PRODUCT"),     # "oranges"
#                 (22, 26, "QUANTITY"),    # "200g"
#                 (27, 33, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "We ate 5 grapes with 50ml juice",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "5"
#                 (9, 14, "PRODUCT"),      # "grapes"
#                 (20, 24, "QUANTITY"),    # "50ml"
#                 (25, 30, "PRODUCT")      # "juice"
#             ]
#         }
#     ),
#     (
#         "He ate 4 mangoes or 2 bananas",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "4"
#                 (9, 16, "PRODUCT"),      # "mangoes"
#                 (20, 21, "QUANTITY"),    # "2"
#                 (22, 29, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "They had 6 strawberries and 2 cups of yogurt",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "6"
#                 (11, 22, "PRODUCT"),     # "strawberries"
#                 (27, 28, "QUANTITY"),    # "2"
#                 (29, 33, "PRODUCT")      # "cups"
#                 # Note: "of yogurt" can be considered part of the product, but spans need adjustment
#             ]
#         }
#     ),
#     (
#         "I ate 1 apple with 30 gm cheese",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "1"
#                 (8, 13, "PRODUCT"),      # "apple"
#                 (19, 24, "QUANTITY"),    # "30g"
#                 (25, 31, "PRODUCT")      # "cheese"
#             ]
#         }
#     ),
#     (
#         "She had 10 grapes or 5 peaches",
#         {
#             'entities': [
#                 (8, 10, "QUANTITY"),     # "10"
#                 (11, 17, "PRODUCT"),     # "grapes"
#                 (22, 23, "QUANTITY"),    # "5"
#                 (24, 31, "PRODUCT")      # "peaches"
#             ]
#         }
#     ),
#     (
#         "We ate 3 plums and 100 g strawberries",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 14, "PRODUCT"),      # "plums"
#                 (19, 24, "QUANTITY"),    # "100g"
#                 (25, 36, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "They ate 2 peaches with 150ml milk",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "2"
#                 (11, 18, "PRODUCT"),     # "peaches"
#                 (24, 29, "QUANTITY"),    # "150ml"
#                 (30, 34, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "I had 4 apricots or 200 g apples",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "4"
#                 (8, 16, "PRODUCT"),      # "apricots"
#                 (21, 26, "QUANTITY"),    # "200g"
#                 (27, 33, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "He ate 5 bananas and 300ml yogurt",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "5"
#                 (9, 16, "PRODUCT"),      # "bananas"
#                 (21, 26, "QUANTITY"),    # "300ml"
#                 (27, 33, "PRODUCT")      # "yogurt"
#             ]
#         }
#     ),
#     (
#         "We had 3 strawberries with 50 gm cream",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 20, "PRODUCT"),      # "strawberries"
#                 (26, 31, "QUANTITY"),    # "50g"
#                 (33, 37, "PRODUCT")      # "cream"
#             ]
#         }
#     ),
#     (
#         "She ate 7 peaches and 100g grapes",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "7"
#                 (10, 17, "PRODUCT"),     # "peaches"
#                 (22, 26, "QUANTITY"),    # "100g"
#                 (27, 33, "PRODUCT")      # "grapes"
#             ]
#         }
#     ),
#     (
#         "I had 1 pear with 100ml milk",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "1"
#                 (8, 12, "PRODUCT"),      # "pear"
#                 (18, 23, "QUANTITY"),    # "100ml"
#                 (24, 28, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "They ate 8 plums or 10 strawberries",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "8"
#                 (11, 16, "PRODUCT"),     # "plums"
#                 (21, 23, "QUANTITY"),    # "10"
#                 (24, 36, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "We ate 12 apples and 200 gm yogurt",
#         {
#             'entities': [
#                 (7, 9, "QUANTITY"),      # "12"
#                 (10, 15, "PRODUCT"),     # "apples"
#                 (20, 26, "QUANTITY"),    # "200g"
#                 (27, 33, "PRODUCT")      # "yogurt"
#             ]
#         }
#     ),
#     (
#         "She ate 5 bananas with 150g chocolate",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "5"
#                 (10, 17, "PRODUCT"),     # "bananas"
#                 (23, 27, "QUANTITY"),    # "150g"
#                 (28, 37, "PRODUCT")      # "chocolate"
#             ]
#         }
#     ),
#     (
#         "I had 6 grapes and 300g mangoes",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "6"
#                 (8, 13, "PRODUCT"),      # "grapes"
#                 (18, 22, "QUANTITY"),    # "300g"
#                 (23, 30, "PRODUCT")      # "mangoes"
#             ]
#         }
#     ),
#     (
#         "He ate 3 strawberries or 50ml honey",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 20, "PRODUCT"),      # "strawberries"
#                 (24, 28, "QUANTITY"),    # "50ml"
#                 (29, 34, "PRODUCT")      # "honey"
#             ]
#         }
#     ),
#     (
#         "We ate 8 apples with 250ml milk",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "8"
#                 (9, 14, "PRODUCT"),      # "apples"
#                 (20, 25, "QUANTITY"),    # "250ml"
#                 (26, 30, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "I had 4 oranges and 100g yogurt",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "4"
#                 (8, 15, "PRODUCT"),      # "oranges"
#                 (20, 24, "QUANTITY"),    # "100g"
#                 (25, 31, "PRODUCT")      # "yogurt"
#             ]
#         }
#     ),
#     (
#         "They ate 3 peaches or 100g grapes",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "3"
#                 (11, 18, "PRODUCT"),     # "peaches"
#                 (23, 27, "QUANTITY"),    # "100g"
#                 (28, 34, "PRODUCT")      # "grapes"
#             ]
#         }
#     ),
#     (
#         "She ate 7 apples and 100ml juice",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "7"
#                 (10, 15, "PRODUCT"),     # "apples"
#                 (20, 25, "QUANTITY"),    # "100ml"
#                 (26, 31, "PRODUCT")      # "juice"
#             ]
#         }
#     ),
#     (
#         "I had 3 grapes with 200g strawberries",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "3"
#                 (8, 13, "PRODUCT"),      # "grapes"
#                 (19, 23, "QUANTITY"),    # "200g"
#                 (24, 35, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "They had 10 apricots and 50ml cream",
#         {
#             'entities': [
#                 (9, 11, "QUANTITY"),     # "10"
#                 (12, 20, "PRODUCT"),     # "apricots"
#                 (25, 29, "QUANTITY"),    # "50ml"
#                 (30, 35, "PRODUCT")      # "cream"
#             ]
#         }
#     ),
#     (
#         "I ate 2 strawberries with 150g milk",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "2"
#                 (8, 19, "PRODUCT"),      # "strawberries"
#                 (25, 29, "QUANTITY"),    # "150g"
#                 (30, 34, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "We had 5 peaches or 3 apricots",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "5"
#                 (9, 16, "PRODUCT"),      # "peaches"
#                 (21, 22, "QUANTITY"),    # "3"
#                 (23, 31, "PRODUCT")      # "apricots"
#             ]
#         }
#     ),
#     (
#         "She ate 2 bananas with 100g chocolate",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "2"
#                 (10, 17, "PRODUCT"),     # "bananas"
#                 (23, 27, "QUANTITY"),    # "100g"
#                 (28, 37, "PRODUCT")      # "chocolate"
#             ]
#         }
#     ),
#     (
#         "I had 5 apples and 2 strawberries",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "5"
#                 (8, 13, "PRODUCT"),      # "apples"
#                 (18, 19, "QUANTITY"),    # "2"
#                 (20, 31, "PRODUCT")      # "strawberries"
#             ]
#         }
#     ),
#     (
#         "We ate 3 plums or 50 gm grapes",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 14, "PRODUCT"),      # "plums"
#                 (19, 24, "QUANTITY"),    # "50g"
#                 (25, 31, "PRODUCT")      # "grapes"
#             ]
#         }
#     ),
#     (
#         "They had 6 bananas with 300ml milk",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "6"
#                 (11, 18, "PRODUCT"),     # "bananas"
#                 (24, 29, "QUANTITY"),    # "300ml"
#                 (30, 34, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
#     (
#         "She ate 10 strawberries or 2 apples",
#         {
#             'entities': [
#                 (8, 10, "QUANTITY"),     # "10"
#                 (11, 22, "PRODUCT"),     # "strawberries"
#                 (27, 28, "QUANTITY"),    # "2"
#                 (29, 34, "PRODUCT")      # "apples"
#             ]
#         }
#     ),
#     (
#         "I had 4 oranges with 200 gm yogurt",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "4"
#                 (8, 15, "PRODUCT"),      # "oranges"
#                 (21, 27, "QUANTITY"),    # "200g"
#                 (28, 34, "PRODUCT")      # "yogurt"
#             ]
#         }
#     ),
#     (
#         "We ate 3 bananas with 100ml juice",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "3"
#                 (9, 16, "PRODUCT"),      # "bananas"
#                 (22, 27, "QUANTITY"),    # "100ml"
#                 (28, 33, "PRODUCT")      # "juice"
#             ]
#         }
#     ),
#     (
#         "He had 2 grapes and 5 bananas",
#         {
#             'entities': [
#                 (7, 8, "QUANTITY"),      # "2"
#                 (9, 14, "PRODUCT"),      # "grapes"
#                 (19, 20, "QUANTITY"),    # "5"
#                 (21, 28, "PRODUCT")      # "bananas"
#             ]
#         }
#     ),
#     (
#         "She ate 8 plums with 100g yogurt",
#         {
#             'entities': [
#                 (8, 9, "QUANTITY"),      # "8"
#                 (10, 15, "PRODUCT"),     # "plums"
#                 (21, 25, "QUANTITY"),    # "100g"
#                 (26, 32, "PRODUCT")      # "yogurt"
#             ]
#         }
#     ),
#     (
#         "I had 3 oranges and 150ml juice",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "3"
#                 (8, 15, "PRODUCT"),      # "oranges"
#                 (20, 25, "QUANTITY"),    # "150ml"
#                 (26, 31, "PRODUCT")      # "juice"
#             ]
#         }
#     ),
#     (
#         "They ate 6 strawberries with 200g cream",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),     # "6"
#                 (11, 22, "PRODUCT"),     # "strawberries"
#                 (28, 31, "QUANTITY"),    # "200g"
#                 (32, 37, "PRODUCT")      # "cream"
#             ]
#         }
#     ),
#     (
#         "I had 7 bananas or 200ml milk",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),      # "7"
#                 (8, 15, "PRODUCT"),      # "bananas"
#                 (19, 24, "QUANTITY"),    # "200ml"
#                 (25, 29, "PRODUCT")      # "milk"
#             ]
#         }
#     ),
# ]

# import spacy
# from spacy.training import Example
# import random

# # Training data
# train_data = [
#     (
#         "They ate 6 strawberries with 200g cream",
#         {
#             'entities': [
#                 (9, 10, "QUANTITY"),
#                 (11, 23, "PRODUCT"),
#                 (29, 33, "QUANTITY"),
#                 (34, 39, "PRODUCT")
#             ]
#         }
#     ),
#     (
#         "I had 7 bananas or 200ml milk",
#         {
#             'entities': [
#                 (6, 7, "QUANTITY"),
#                 (8, 15, "PRODUCT"),
#                 (19, 24, "QUANTITY"),
#                 (25, 29, "PRODUCT")
#             ]
#         }
#     ),
#     # Add more training examples for better performance
# ]

# # Load the pre-trained model
# nlp = spacy.load('custom_ner_model')

# # Get the NER component
# if 'ner' not in nlp.pipe_names:
#     ner = nlp.add_pipe('ner')
# else:
#     ner = nlp.get_pipe('ner')

# # Add new labels to the NER
# for _, annotations in train_data:
#     for ent in annotations.get('entities'):
#         ner.add_label(ent[2])

# # Disable other pipeline components and train the NER
# other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
# with nlp.disable_pipes(*other_pipes):
#     optimizer = nlp.resume_training()
#     optimizer.learn_rate = 0.00001  # Optional: Set learning rate

#     epochs = 200
#     for epoch in range(epochs):
#         random.shuffle(train_data)
#         losses = {}
#         for text, annotations in train_data:
#             doc = nlp.make_doc(text)
#             example = Example.from_dict(doc, annotations)
#             nlp.update(
#                 [example],
#                 sgd=optimizer,
#                 drop=0.5,
#                 losses=losses
#             )
#         print(f'Epoch {epoch + 1}, Losses: {losses}')



import spacy

# Save the trained model
# nlp.to_disk('custom_ner_model')

# Load the trained model
trained_nlp = spacy.load('custom_ner_model1')

# Test data
# test_texts = [
#     "They ate 6 strawberries and 2 bananas with 200g cream",
#     "I had 7 bananas or 200ml milk",
#     "He bought 3 apples and 500g yogurt",
#     "gaurav eat 10 eggs with 200ml milk",
#     'vivek eat 20 mangoes',
#     '10 gm mangoes, 20 gm apples, 30 gm milk, 3 egges'
# ]

# test_texts = [input()]
#
#
# # Test the trained model
# def food(input_text):
#     doc = trained_nlp(input_text)
#     print(f'\nText: "{input_text}"')
#     ans = []
#     for ent in doc.ents:
#         ans.append({'Entity': ent.text, 'Label': ent.label_})
#
#     return ans

#
# from flask import Flask, request, jsonify
#
# app = Flask(__name__)
#
# # Dummy function simulating NLP processing
def food(input_text):
    # Simulated NLP model output (Replace with your actual NLP model)
    doc = trained_nlp(input_text)  # Ensure trained_nlp is defined
    ans = [{'Entity': ent.text, 'Label': ent.label_} for ent in doc.ents]
    # for new_dict in ans:
    #     if new_dict['Entity'] != None:
    return ans

print(food('i ate mango and apple'))
#
# print(food('i ate one mango and one apple '))
# @app.route('/api/food_api', methods=['POST'])
# def process_text():
#     data = request.json
#     # print(data)
#     if not data or 'text' not in data:
#         return jsonify({'error': 'Text input is required'}), 400
#
#
#     input_text = data['text']
#     result = food(input_text)
#     return jsonify({'input': input_text, 'entities': result})
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
#
food('eat 100 g rice')
def extract_entities(input_text):
    doc = trained_nlp(input_text)  # Run NLP model
    entities = [{'Entity': ent.text, 'Label': ent.label_} for ent in doc.ents]  # Convert to list for easier processing
    print(entities)
    result = []  # Store final output
    last_quantity = None  # Track last seen QUANTITY

    for ent in entities:
        if ent['Label'] == "QUANTITY":
            last_quantity = ent['Entity']  # Store quantity to assign to next product
        elif ent['Label'] == "PRODUCT":
            result.append({'Entity': ent['Entity'], 'Quantity': last_quantity})
            last_quantity = None  # Reset after assigning to a product
    # [{Entity: 'mango', Quantity: 'one'}, {Entity: 'apple', Quantity: None}]
    return result

print(extract_entities('eat 100 g rice'))
food('eat 100 g rice')