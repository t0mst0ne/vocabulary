import json
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

# Ensure necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    print("Downloading NLTK data...")
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN # Default

def find_target_in_example(word, example):
    # 1. Exact match (case insensitive)
    if word.lower() in example.lower().split():
        # Find the exact casing used
        for w in example.split():
            if w.lower() == word.lower():
                return w
                
    # 2. Lemmatization match
    tokens = word_tokenize(example)
    pos_tags = nltk.pos_tag(tokens)
    
    for token, tag in pos_tags:
        # Skip punctuation
        if not token.isalnum():
            continue
            
        wn_pos = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(token.lower(), wn_pos)
        
        if lemma == word.lower():
            return token
            
        # Try default noun lemmatization if verb failed, or vice versa
        if lemmatizer.lemmatize(token.lower(), wordnet.VERB) == word.lower():
            return token
        if lemmatizer.lemmatize(token.lower(), wordnet.NOUN) == word.lower():
            return token

    # 3. Substring match (risky but useful for plurals like "aboriginals")
    # Only if word length > 3 to avoid matching "a" in "apple"
    if len(word) > 3:
        for token in tokens:
            if token.lower().startswith(word.lower()):
                return token
                
    return None

def enrich_data():
    print("Loading data/words.json...")
    with open('data/words.json', 'r') as f:
        words = json.load(f)
        
    updated_count = 0
    
    print(f"Processing {len(words)} words...")
    
    for i, word_data in enumerate(words):
        if i % 500 == 0:
            print(f"Processed {i}...")
            
        word = word_data.get('word', '')
        if not word:
            continue
            
        # Find best example (logic similar to script.js)
        selected_example = None
        
        # 1. Cambridge
        if 'cambridge' in word_data and 'meanings' in word_data['cambridge']:
            for m in word_data['cambridge']['meanings']:
                if m.get('examples') and len(m['examples']) > 0:
                    selected_example = m['examples'][0]
                    break
        
        # 2. Analysis
        if not selected_example and 'analysis' in word_data and word_data['analysis']:
            analysis = word_data['analysis']
            if 'less_common_meanings' in analysis:
                for m in analysis['less_common_meanings']:
                    if m.get('example'):
                        selected_example = m['example']
                        break
            if not selected_example and 'most_common_meaning' in analysis:
                if analysis['most_common_meaning'].get('example'):
                    selected_example = analysis['most_common_meaning']['example']
                    
        if selected_example:
            target = find_target_in_example(word, selected_example)
            if target:
                word_data['quiz'] = {
                    "example": selected_example,
                    "target_word": target
                }
                updated_count += 1
            else:
                # print(f"Failed to find '{word}' in '{selected_example}'")
                pass
                
    print(f"Enriched {updated_count} words with quiz data.")
    
    print("Saving to data/words.json...")
    with open('data/words.json', 'w') as f:
        json.dump(words, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    enrich_data()
