# Script to generate levels for a word game using NLTK's words corpus

import json
import random
from nltk.corpus import words
import nltk

# Donload from the Dictionay NLTK
nltk.download("words")
word_list = list(set(words.words()))
random.shuffle(word_list)

# Classify words according to their length
easy_words = [w.lower() for w in word_list if 3 <= len(w) <= 5 and w.isalpha()] # 3-5 letters
medium_words = [w.lower() for w in word_list if 6 <= len(w) <= 8 and w.isalpha()]   # 6-8 letters
hard_words = [w.lower() for w in word_list if len(w) >= 9 and w.isalpha()]       # 9+ letters

# Rmove duplicates
def unique_words(word_list):
    seen = set()
    unique = []
    for word in word_list:
        if word not in seen:
            seen.add(word)
            unique.append(word)
    return unique

easy_words = unique_words(easy_words)
medium_words = unique_words(medium_words)
hard_words = unique_words(hard_words)

# build levels for each category
# Each level contains 50 words, and if the number of words is less than 50, fill the rest with random words from the same category
def build_levels(words, per_level=50, total_levels=100):
    levels = {"levels": []}
    start = 0
    for _ in range(total_levels):
        chunk = words[start:start+per_level]
        if len(chunk) < per_level:
            chunk += random.choices(words, k=per_level - len(chunk))
        levels["levels"].append(chunk)
        start += per_level
    return levels

easy_levels = build_levels(easy_words)
medium_levels = build_levels(medium_words)
hard_levels = build_levels(hard_words)

# Save them as JSON files
with open("easy.json", "w") as f:
    json.dump(easy_levels, f, indent=2)
with open("medium.json", "w") as f:
    json.dump(medium_levels, f, indent=2)
with open("hard.json", "w") as f:
    json.dump(hard_levels, f, indent=2)

print("✅ files easy.json، medium.json، hard.json had Successfully Generated !")
