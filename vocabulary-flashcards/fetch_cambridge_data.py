import json
import requests
from bs4 import BeautifulSoup
import time
import random
import os

INPUT_FILE = 'data/words.json'
OUTPUT_FILE = 'data/words.json' # We will update in place or create a new one? Let's update in place carefully.

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_cambridge_data(word):
    url = f"https://dictionary.cambridge.org/dictionary/english-chinese-traditional/{word}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 404:
            print(f"Word not found: {word}")
            return None
        if response.status_code != 200:
            print(f"Error fetching {word}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first entry block
        entry_body = soup.find(class_='di-body') or soup.find(class_='def-block')
        
        if not entry_body:
            return None

        # Extract definitions and examples
        meanings = []
        
        def_blocks = entry_body.find_all(class_='def-block')
        
        for block in def_blocks:
            # Definition Header
            def_head = block.find(class_='ddef_h')
            if not def_head: continue
            
            # English Definition
            def_node = def_head.find(class_='ddef_d')
            if not def_node: continue
            
            definition_text = def_node.get_text(separator=' ', strip=True)
            
            # Definition Body (contains translation and examples)
            def_body = block.find(class_='def-body')
            if not def_body: continue

            # Chinese Translation (First .trans in body)
            trans_node = def_body.find(class_='trans')
            translation_text = trans_node.get_text(separator=' ', strip=True) if trans_node else ""
            
            full_definition = f"{translation_text} ({definition_text})" if translation_text else definition_text
            
            # Examples
            examples = []
            examp_nodes = def_body.find_all(class_='examp')
            for ex in examp_nodes:
                eg_node = ex.find(class_='eg')
                
                if eg_node:
                    eg_text = eg_node.get_text(separator=' ', strip=True)
                    # User requested NO Chinese in examples for the quiz
                    examples.append(eg_text)
            
            if examples:
                meanings.append({
                    "definition": full_definition,
                    "examples": examples
                })
        
        if not meanings:
            return None
            
        return {
            "meanings": meanings,
            "url": url
        }

    except Exception as e:
        print(f"Exception fetching {word}: {e}")
        return None

def main():
    print("Loading words...")
    try:
        with open(INPUT_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("data/words.json not found!")
        return

    print(f"Total words: {len(data)}")
    
    # Filter for words that don't have cambridge data yet
    # For testing, let's just do a small batch if the user wants, but the goal is to do all.
    # We will save incrementally.
    
    count = 0
    updated_count = 0
    
    # Shuffle to get a random sample if we stop early, or just iterate.
    # Let's iterate linearly to be consistent.
    
    for item in data:
        word = item['word']
        
        # Skip if already has cambridge data (unless we want to force update)
        # FORCE UPDATE enabled to fix broken data
        # if 'cambridge' in item and item['cambridge']:
        #    continue
            
        print(f"Fetching: {word}...")
        cambridge_data = fetch_cambridge_data(word)
        
        if cambridge_data:
            item['cambridge'] = cambridge_data
            updated_count += 1
            print(f"  -> Found {len(cambridge_data['meanings'])} meanings.")
        else:
            print("  -> No data found.")
            # Mark as checked so we don't retry immediately? 
            # item['cambridge'] = None 
        
        count += 1
        
        # Save every 10 words to avoid data loss
        if count % 10 == 0:
            print(f"Saving progress... ({updated_count} updated so far)")
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Be nice to the server
        time.sleep(random.uniform(1.0, 2.5))
        
        # Safety break for testing - REMOVE THIS FOR FULL RUN
        if count >= 50: 
           break

    # Final save
    print("Final save...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    main()
