from symspellpy import SymSpell, Verbosity

# Initialize SymSpell
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Load pre-trained English dictionary
if not sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", term_index=0, count_index=1):
    print("Dictionary file not found!")

# Add custom Hinglish words with frequency
with open('names.txt', 'r', encoding='utf-8') as file:
    for line in file:
        word = line.strip().lower()  # Read and clean each word
        if word:  # Avoid empty lines
            sym_spell.create_dictionary_entry(word, 150)

# Test correction
text = "I love panner tikka and biryanii"
suggestions = sym_spell.lookup_compound(text, max_edit_distance=2)

# Save the dictionary
sym_spell.save_pickle('new_dictionary.pickle')

# Print corrected text
if suggestions:
    print(suggestions[0].term)  # Expected: "I love paneer tikka and biryani"
