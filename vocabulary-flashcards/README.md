# Vocabulary Flashcards
A web-based vocabulary flashcard application designed for students to learn English words efficiently.

## Live Demo
[View on GitHub Pages](https://t0mst0ne.github.io/vocabulary/vocabulary-flashcards/)

> **Note:** The "View on Merriam-Webster/Cambridge" preview feature requires a backend proxy and will not work on the static GitHub Pages deployment. Please use the "View on..." buttons to open the dictionary in a new tab.

## Features

- **Interactive Flashcards**: Flip cards to see definitions, examples, and word analysis.
- **Quiz Mode**: Test your knowledge with multiple-choice questions.
- **Highlight to Search**: Select any text on the page to instantly search it in the Cambridge Dictionary.
- **Dictionary Integration**: View embedded content from Cambridge Dictionary and Merriam-Webster (Localhost only).
- **Progress Tracking**: Your quiz mistakes are saved locally so you can review them later.

## How to Use

### 1. GitHub Pages (Online)

You can access the live version of the app here:
**[https://t0mst0ne.github.io/vocabulary/vocabulary-flashcards/index.html](https://t0mst0ne.github.io/vocabulary/vocabulary-flashcards/index.html)**

> **Note**: On the static GitHub Pages site, the embedded dictionary preview on the back of the card will not load because it requires a backend proxy to bypass browser security (CORS). However, the **Highlight to Search** feature works perfectly, and you can click the "View on..." buttons to open dictionaries in a new tab.

### 2. Localhost (Full Features)

To use the application with **full functionality** (including the embedded dictionary lookups on the back of the card), you need to run the included local server.

#### Prerequisites
- Python 3 installed on your machine.

#### Steps
1.  Clone the repository:
    ```bash
    git clone https://github.com/t0mst0ne/vocabulary.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd vocabulary/vocabulary-flashcards
    ```
3.  Start the custom proxy server:
    ```bash
    python3 server.py
    ```
4.  Open your browser and go to:
    **[http://localhost:8000](http://localhost:8000)**

## Project Structure

- `index.html`: Main entry point for the website.
- `script.js`: Contains all the application logic, including flashcard handling, quiz generation, and the proxy fetcher.
- `style.css`: Styling for the application.
- `server.py`: A simple Python HTTP server with a proxy endpoint to handle CORS for dictionary requests.
- `data/words.json`: The vocabulary data source.
