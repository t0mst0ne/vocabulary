import json
import os
from PIL import Image, ImageDraw

# 1. Populate words.json
extracted_file = '../extracted.txt'
json_file = 'data/words.json'

# Read existing JSON
try:
    with open(json_file, 'r') as f:
        existing_data = json.load(f)
except FileNotFoundError:
    existing_data = []

existing_words = {item['word'] for item in existing_data}

# Read extracted.txt
new_words = []
with open(extracted_file, 'r') as f:
    for line in f:
        word = line.strip()
        if word and word not in existing_words:
            new_words.append({
                "word": word,
                "analysis": None # No detailed analysis for these yet
            })

# Combine and save
all_data = existing_data + new_words
with open(json_file, 'w') as f:
    json.dump(all_data, f, indent=2)

print(f"Added {len(new_words)} new words. Total words: {len(all_data)}")

# 2. Generate Icons
icon_sizes = [16, 48, 128]
if not os.path.exists('images'):
    os.makedirs('images')

for size in icon_sizes:
    img = Image.new('RGB', (size, size), color = (99, 102, 241)) # Indigo color
    d = ImageDraw.Draw(img)
    d.text((size//4, size//4), "V", fill=(255, 255, 255))
    img.save(f'images/icon{size}.png')

print("Icons generated.")
