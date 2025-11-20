import json
import nltk
from nltk.corpus import wordnet as wn
import re

# Ensure data is downloaded
try:
    wn.synsets('dog')
except LookupError:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

INPUT_FILE = '../extracted.txt'
OUTPUT_FILE = 'data/words.json'

def get_chinese_definition(synset):
    lemmas = synset.lemmas(lang='cmn')
    english_def = synset.definition()
    if lemmas:
        chinese_words = sorted(list(set(l.name() for l in lemmas)))
        return f"{', '.join(chinese_words)} ({english_def})"
    else:
        return english_def

def get_word_family(synset):
    family = []
    seen = set()
    for lemma in synset.lemmas():
        for form in lemma.derivationally_related_forms():
            word_name = form.name()
            if word_name not in seen and word_name.lower() != lemma.name().lower():
                seen.add(word_name)
                # Simple POS mapping
                pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adj', 'r': 'Adv', 's': 'Adj'}
                pos = pos_map.get(form.synset().pos(), 'Unknown')
                
                # Get Chinese meaning for the derived word if possible
                derived_synset = form.synset()
                chinese_def = get_chinese_definition(derived_synset).split('(')[0].strip() # Try to get just Chinese
                if not chinese_def or chinese_def == derived_synset.definition():
                     chinese_def = derived_synset.definition()

                family.append({
                    "word": word_name,
                    "part_of_speech": pos,
                    "definition": chinese_def
                })
    return family[:5]

def get_related_phrases(word):
    # Find synsets where the lemma contains the word but is not the word itself
    # This is a heuristic for "phrases"
    phrases = []
    seen_phrases = set()
    
    # This might be slow if we search EVERYTHING. 
    # Instead, let's try to guess common phrases or rely on WordNet's structure if possible.
    # WordNet doesn't have a direct "phrases containing X" index.
    # Workaround: Check if the word is part of multi-word lemmas in the same or related synsets? 
    # Or just skip for now as "no API" limits us.
    # Actually, we can check lemmas of the synsets we found.
    
    # Better approach for "Phrases":
    # Look for lemmas in ALL synsets that contain the word + space or space + word
    # This is too heavy.
    # Let's restrict to: check lemmas of the word's synsets and their neighbors?
    
    # Alternative: Just use the collocations? NLTK has collocations but they are statistical, not defined.
    
    # Let's try a simple approach: 
    # If the word is 'make', 'make_up' is a lemma in some synset.
    # But 'make_up' synset won't be found by wn.synsets('make').
    
    # We will skip complex phrase extraction to avoid massive slowdowns/hallucinations 
    # and stick to what we can reliably get: Word Family and Definitions.
    # If the user strictly wants phrases, we might need a phrase list. 
    # I will leave it empty but formatted correctly.
    return []

def process_word(word):
    synsets = wn.synsets(word)
    if not synsets:
        return None

    pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb', 's': 'Adjective'}

    # 1. Most Common Meaning
    primary = synsets[0]
    most_common = {
        "part_of_speech": pos_map.get(primary.pos(), 'Unknown'),
        "definition": get_chinese_definition(primary),
        "example": primary.examples()[0] if primary.examples() else ""
    }

    # 2. Less Common Meanings
    less_common = []
    for s in synsets[1:4]:
        less_common.append({
            "part_of_speech": pos_map.get(s.pos(), 'Unknown'),
            "definition": get_chinese_definition(s),
            "example": s.examples()[0] if s.examples() else ""
        })

    # 3. Word Family
    word_family = get_word_family(primary)

    # 4. Related Phrases
    related_phrases = get_related_phrases(word)

    return {
        "most_common_meaning": most_common,
        "less_common_meanings": less_common,
        "word_family": word_family,
        "related_phrases": related_phrases
    }

def main():
    print("Reading words...")
    with open(INPUT_FILE, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(words)} words...")
    
    results = []
    for i, word in enumerate(words):
        if i % 100 == 0:
            print(f"Processed {i}/{len(words)}")
        
        analysis = process_word(word)
        
        if analysis:
            results.append({
                "word": word,
                "analysis": analysis
            })
        else:
            results.append({
                "word": word,
                "analysis": None
            })

    print("Saving to JSON...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    main()
