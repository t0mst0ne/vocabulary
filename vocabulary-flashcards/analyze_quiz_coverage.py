import json
import re

def analyze_coverage():
    try:
        with open('data/words.json', 'r') as f:
            words = json.load(f)
    except FileNotFoundError:
        print("Error: data/words.json not found.")
        return

    total_words = len(words)
    quizzable_count = 0
    reasons = {
        "no_example": 0,
        "regex_fail": 0,
        "ok": 0
    }

    print(f"Total words: {total_words}")

    for word_data in words:
        word = word_data.get('word', '')
        if not word:
            continue

        # Logic from script.js to find a valid meaning with example
        selected_meaning = None
        
        # Check for pre-calculated quiz data
        if 'quiz' in word_data and word_data['quiz'].get('target_word'):
             reasons["ok"] += 1
             quizzable_count += 1
        else:
             # Fallback check (simplified)
             reasons["no_example"] += 1

    print("-" * 20)
    print(f"Quizzable Words (Enriched): {quizzable_count} ({quizzable_count/total_words*100:.2f}%)")
    print(f"Failed (No Quiz Data): {reasons['no_example']}")
    print("-" * 20)

if __name__ == "__main__":
    analyze_coverage()
