import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("Downloading WordNet data...")
try:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    print("Download complete.")
except Exception as e:
    print(f"Error downloading: {e}")

from nltk.corpus import wordnet as wn

word = 'flea'
print(f"\nTesting word: {word}")
synsets = wn.synsets(word)

if not synsets:
    print("No synsets found.")
else:
    for s in synsets[:3]:
        print(f"\nSynset: {s.name()}")
        print(f"Definition: {s.definition()}")
        print(f"Examples: {s.examples()}")
        chinese_lemmas = s.lemmas(lang='cmn')
        print(f"Chinese Lemmas: {[l.name() for l in chinese_lemmas]}")
