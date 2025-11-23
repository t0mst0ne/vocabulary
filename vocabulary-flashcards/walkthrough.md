# Quiz Generation Improvements

I have updated the application to "generate as more quiz as possible" by improving the data processing and quiz generation logic.

## Changes Made

1.  **Enriched Data (`data/words.json`)**:
    -   Created `enrich_quiz_data.py` to pre-process the vocabulary list.
    -   Used NLTK (Natural Language Toolkit) to analyze example sentences.
    -   Identified the exact form of the word used in examples (e.g., matching "running" for the word "run").
    -   Added a new `quiz` field to `words.json` containing the `example` and the specific `target_word` to mask.

2.  **Updated Frontend (`script.js`)**:
    -   Refactored `generateQuestion` to prioritize the pre-calculated `quiz` data.
    -   This ensures that even if the word form differs from the base word (morphology), the quiz correctly masks it.
    -   Maintained fallback logic for the few words without pre-calculated data.

## Results

-   **Initial Coverage**: ~73% (4485 words) were valid for quizzes using simple regex.
-   **New Coverage**: **94.56% (5791 words)** are now valid for quizzes.
-   **Improvement**: Added **1306** new valid quiz questions.

## Verification

-   Ran `analyze_quiz_coverage.py` to verify the data enrichment.
-   Confirmed that `words.json` now contains the `quiz` field for 5791 entries.
