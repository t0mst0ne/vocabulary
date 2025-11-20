import re

INPUT_FILE = 'temp_words.txt'
OUTPUT_FILE = 'extracted.txt'

def parse_word_token(token):
    """
    Parses a single word token like 'agree(ment)' or 'bicycle' or 'ad'.
    Returns a list of expanded words.
    """
    words = []
    
    # Handle parenthesis expansion: agree(ment) -> agree, agreement
    # Regex to find (suffix) at the end
    match = re.search(r'([a-zA-Z0-9\-\'’]+)\(([a-zA-Z0-9]+)\)$', token)
    if match:
        base = match.group(1)
        suffix = match.group(2)
        words.append(base)
        words.append(base + suffix)
    else:
        # Just a normal word (or one with internal parens we don't handle? usually suffixes are at end)
        # Remove any other parens if they exist?
        # The PDF says "argue (argument)". It seems they are space separated in description but in list?
        # List: "agree(ment)" (no space).
        # Let's assume clean token.
        words.append(token.replace('(', '').replace(')', '')) 

    return words

def process_line(line):
    # Regex to find the word part at the start of the line
    # It stops before the Part of Speech (n., v., etc.)
    # POS tags: n., v., adj., adv., prep., conj., pron., aux., art., num.
    # Note: Sometimes there are multiple POS separated by / like n./v.
    
    # Pattern: Start of line, capture characters until we hit a space followed by a POS-like pattern
    # POS pattern: (?:n|v|adj|adv|prep|conj|pron|aux|art|num)\.
    
    match = re.match(r'^\s*([a-zA-Z0-9\-\/\'’()]+)\s+(?:n|v|adj|adv|prep|conj|pron|aux|art|num)', line)
    if match:
        raw_token = match.group(1)
        
        # Split by slash first: advertise(ment)/ad -> advertise(ment), ad
        tokens = raw_token.split('/')
        
        final_words = []
        for t in tokens:
            final_words.extend(parse_word_token(t))
            
        return final_words
    return []

def main():
    print(f"Reading {INPUT_FILE}...")
    all_words = set()
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            extracted = process_line(line)
            for w in extracted:
                # Clean up
                w = w.strip()
                # Filter out empty or non-word junk
                if w and not w.isdigit():
                    all_words.add(w)

    print(f"Extracted {len(all_words)} unique words.")
    
    # Sort alphabetically
    sorted_words = sorted(list(all_words), key=lambda s: s.lower())
    
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for w in sorted_words:
            f.write(w + '\n')
            
    print("Done.")

if __name__ == "__main__":
    main()
