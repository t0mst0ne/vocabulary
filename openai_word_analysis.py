import os
import time
from openai import OpenAI

# Base prompt template inspired by gemini.md
PROMPT_TEMPLATE = """
你是一位專為大學學測考生設計的英文詞彙專家。你的任務是針對一個核心單字，進行全面且深入的分析，包含其多種詞義、字根衍生字、以及相關片語。

相當接使用LLM 不要再寫 script
請針對我提供的單字："{word}"，依照以下格式提供分析：

1. **主要意思 (Most Common Meaning):**
    * **詞性:** (Part of Speech)
    * **定義:** (Definition in Chinese)
    * **例句:** (Example sentence in English, with Chinese translation)

2. **次要/不常見意思 (Less Common Meanings):**
    * 請以條列方式，列出該單字的其他意思。
    * 對於每一個意思，都必須包含以下三項資訊：
        * **詞性:** (Part of Speech)
        * **定義:** (Definition in Chinese)
        * **例句:** (Example sentence in English, with Chinese translation)

3. **相關衍生字 (Word Family):**
    * 請列出由相同字根衍生的其他單字，並提供其詞性與中文意思。
    * 格式：`[單字] ([詞性]): [中文意思]`

4. **相關片語/慣用語 (Related Phrases/Idioms):**
    * 請以條列方式，列出包含此單字的常見片語或慣用語。
    * 對於每一個片語，都必須包含以下三項資訊：
        * **片語:** (The phrase itself)
        * **定義:** (Definition in Chinese)
        * **例句:** (Example sentence in English, with Chinese translation)

請確保所有資訊清晰、有條理，且對準備考試的學生有實質幫助。
"""

# Refinement prompt for GPT-4.1
REFINEMENT_PROMPT = """
以下是單字 "{word}" 的初步分析草稿，請你作為英語詞彙專家，仔細校正並改善這個分析。確保資訊準確、中文翻譯正確、格式一致，不能無中生有的片語 然後去權威的線上字典（如 Merriam-Webster, Oxford Learner's Dictionaries, Longman）查證,如果字典裡完全沒有類似的用法，那要排除。

原始草稿：
{draft}

請提供最終的分析版本：
"""

def generate_draft(client, word):
    system_prompt = "You are a vocabulary expert for Taiwanese college entrance exams."
    user_prompt = PROMPT_TEMPLATE.format(word=word)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        response = client.chat.completions.create(
            model="o1-mini",  # Use cheaper model for initial drafts
            messages=[
                {"role": "user", "content": full_prompt}
            ]
            # o1 models control output length internally, no max_tokens needed
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating draft for {word}: {e}")
        return f"Error: {e}"

def refine_analysis(client, word, draft):
    prompt = REFINEMENT_PROMPT.format(word=word, draft=draft)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",  # Use advanced model for refinement
            messages=[
                {"role": "system", "content": "You are a senior vocabulary expert for Taiwanese college entrance exams. Your task is to carefully review and improve word analyses for accuracy and quality."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,  # More tokens for refined analysis
            temperature=0.0  # Deterministic output
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error refining analysis for {word}: {e}")
        return f"Error: {e}"

def main():
    # Read word list
    if not os.path.exists('extracted.txt'):
        print("extracted.txt not found!")
        return

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set the OPENAI_API_KEY environment variable.")
        return

    # Set up OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    with open('extracted.txt', 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]

    draft_dir = 'word_drafts'
    output_dir = 'word_analyses'
    os.makedirs(draft_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Found {len(words)} words to process.")

    # Step 1: Generate drafts with o1-mini
    print("=== Step 1: Generating drafts with o1-mini ===")
    for i, word in enumerate(words):
        print(f"Generating draft {i+1}/{len(words)}: {word}")
        draft = generate_draft(client, word)

        filename = f"{word}.md"
        filepath = os.path.join(draft_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(draft)

        # Rate limit: wait 1 second between requests
        time.sleep(1)

    print("Draft generation complete.")

    # Step 2: Refine drafts with GPT-4.1
    print("=== Step 2: Refining drafts with GPT-4.1 ===")
    for i, word in enumerate(words):
        print(f"Refining analysis {i+1}/{len(words)}: {word}")

        draft_file = os.path.join(draft_dir, f"{word}.md")
        if os.path.exists(draft_file):
            with open(draft_file, 'r', encoding='utf-8') as f:
                draft_content = f.read()
        else:
            draft_content = "Draft not found."

        refined_analysis = refine_analysis(client, word, draft_content)

        filename = f"{word}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {word} 的深度解析\n\n")
            f.write(refined_analysis)

        # Rate limit: wait 2 seconds for the more expensive model
        time.sleep(2)

    print("Analysis refinement complete. Final analyses saved in word_analyses/.")

if __name__ == "__main__":
    main()
