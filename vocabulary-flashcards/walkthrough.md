# Vocabulary Flashcards Extension - Walkthrough

I have created the Chrome Extension for your vocabulary flashcards.

## Features
- **Flashcard UI**: Modern, glassmorphism design.
- **Comprehensive Vocabulary**: 
    - **Source**: Updated from "高中英文參考詞彙表(111學年度起適用)", containing **6124 words**.
    - **Detailed Analysis**: Each card includes the most common meaning, less common meanings, word family, and related phrases.
    - **Offline First**: Core definitions and examples are generated locally using NLTK WordNet. available) and English definitions.
        - **Word Family**: Derived forms included.
        - **Phrases**: (Limited support in offline mode).
    - **External Resources**: 
        - **Cambridge Dictionary**: Direct link and embedded definitions.
        - **Merriam-Webster**: Direct link and embedded definitions from Merriam-Webster.
            - **Clean View**: Distracting links on normal words are removed.
            - **Idioms Preserved**: Links to related idioms and phrases are kept active for easy exploration.
- **Quiz Mode**:
    - Switch to the "Quiz" tab to test your knowledge.
    - **Format**: Multiple Choice (Select the correct **English definition** for the given word).
    - **Advanced Challenge**: The quiz prioritizes **less common meanings** to test deeper understanding.
    - **Reference Context**: A masked **example sentence** is provided to give you context for the specific meaning being tested.
    - **Deep Dive**: Click the **Question Word** itself to instantly switch to the "Learn" tab and see its full analysis and Cambridge Dictionary entry.
    - **Mistake Notebook**: Automatically tracks incorrect answers.
    - **Download**: Click "Download Mistakes" to save your wrong answers as a JSON file for review.
- **Navigation**: 
    - **Randomized Order**: Words are shuffled every time you open the extension to keep your study session fresh.
    - **Controls**: Use Next/Previous buttons to navigate through the shuffled list.
- **Interaction**: Click the card to flip it.

## How to Install on Another Computer (e.g., for your child)

To share this extension with your child, follow these steps:

1.  **Transfer the File**:
    *   I have created a zip file for you: `vocabulary-flashcards.zip`.
    *   Send this file to your child's computer (via email, USB, AirDrop, etc.).

2.  **Unzip**:
    *   On the child's computer, unzip/extract the `vocabulary-flashcards.zip` file. You should see a folder named `vocabulary-flashcards`.

3.  **Load in Chrome**:
    *   Open Google Chrome on the child's computer.
    *   Go to `chrome://extensions/` (type this in the address bar).
    *   Toggle **Developer mode** on (top right corner).
    *   Click **Load unpacked** (top left).
    *   Select the `vocabulary-flashcards` folder you just unzipped.

4.  **Pin the Extension**:
    *   Click the puzzle piece icon in the Chrome toolbar.
    *   Find "Vocabulary Flashcards" and click the pin icon to keep it visible.

Now your child can use the flashcards, take quizzes, and track their progress!ds`.

## How to Use
1. Click the extension icon (a purple "V") in the Chrome toolbar.
2. The popup will open showing the first word ("flea").
3. **Click the card** to flip it and see the detailed analysis.
4. Use **Next/Previous** to navigate through the list.

## Files Created
- `manifest.json`: Extension configuration.
- `popup.html`, `style.css`, `popup.js`: UI and Logic.
- `data/words.json`: The database of words.
- `images/`: Generated icons.
