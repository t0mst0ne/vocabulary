import google.generativeai as genai
import os
import time

# --- 設定 ---
# 1. 請將您從 Google AI Studio 取得的 API 金鑰貼在引號中間
API_KEY = "在這裡貼上您的API金鑰"

# 2. 設定輸入檔案名稱和存放輸出檔案的"資料夾"名稱
INPUT_FILENAME = "extracted.txt"
OUTPUT_DIRECTORY_NAME = "word_analysis_files"
# ---------------

# 使用您的 API 金鑰來設定 genai
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"API 金鑰設定錯誤，請檢查您的金鑰是否正確。錯誤訊息：{e}")
    exit()

# 設定要使用的 AI 模型
model = genai.GenerativeModel('gemini-1.5-flash')

# 指令範本維持不變，一樣用 "||" 分隔，方便程式解析
PROMPT_TEMPLATE = """
你是一位專業的英文詞彙專家「單字庫」。
請針對英文單字 "{word}" 進行全面且深入的分析。
請嚴格依照以下格式回傳結果，並使用 "||" 作為主要分隔符號。

1.  **主要意思**：
    * [詞性]||[中文定義]||[英文例句]||[例句中文翻譯]

2.  **次要意思**：
    * (如果有多個，請用 "|" 分隔每一組)
    * [詞性1]|[中文定義1]|[英文例句1]|[例句翻譯1]|[詞性2]|[中文定義2]...

3.  **相關衍生字**：
    * (如果有多個，請用 "|" 分隔)
    * [單字1] ([詞性1]): [中文意思1]|[單字2] ([詞性2]): [中文意思2]...

4.  **相關片語/慣用語**：
    * (如果有多個，請用 "|" 分隔每一組)
    * [片語1]|[中文定義1]|[英文例句1]|[例句翻譯1]|[片語2]...

如果某個項目沒有內容，請填寫 "無"。
"""

def analyze_word(word):
    """使用 AI 模型分析單一單字"""
    print(f"正在分析單字：{word}...")
    try:
        prompt = PROMPT_TEMPLATE.format(word=word)
        response = model.generate_content(prompt)
        time.sleep(1) # 停頓1秒，避免 API 請求過於頻繁
        return response.text.strip()
    except Exception as e:
        print(f"分析單字 '{word}' 時發生錯誤：{e}")
        return None

def format_as_markdown(word, parts):
    """將解析後的內容格式化為 Markdown 字串"""
    # parts[0]: 主要意思_詞性, parts[1]: 主要意思_定義, etc.
    content = f"# {word.capitalize()}\n\n"

    # 1. 主要意思
    content += "## 1. 主要意思 (Most Common Meaning)\n"
    content += f"- **詞性:** {parts[0]}\n"
    content += f"- **定義:** {parts[1]}\n"
    content += f"- **例句:** {parts[2]}\n"
    content += f"  - (翻譯): {parts[3]}\n\n"

    # 2. 次要意思
    secondary_meanings_raw = parts[4]
    if secondary_meanings_raw != "無":
        content += "## 2. 次要/不常見意思 (Less Common Meanings)\n"
        items = secondary_meanings_raw.split('|')
        # 每4個元素為一組 (詞性, 定義, 例句, 翻譯)
        for i in range(0, len(items), 4):
            if i+3 < len(items):
                content += f"- **詞性:** {items[i].strip()}\n"
                content += f"  - **定義:** {items[i+1].strip()}\n"
                content += f"  - **例句:** {items[i+2].strip()}\n"
                content += f"    - (翻譯): {items[i+3].strip()}\n"
        content += "\n"

    # 3. 相關衍生字
    word_family_raw = parts[5]
    if word_family_raw != "無":
        content += "## 3. 相關衍生字 (Word Family)\n"
        items = word_family_raw.split('|')
        for item in items:
            content += f"- {item.strip()}\n"
        content += "\n"

    # 4. 相關片語
    phrases_raw = parts[6]
    if phrases_raw != "無":
        content += "## 4. 相關片語/慣用語 (Related Phrases/Idioms)\n"
        items = phrases_raw.split('|')
        # 每4個元素為一組 (片語, 定義, 例句, 翻譯)
        for i in range(0, len(items), 4):
             if i+3 < len(items):
                content += f"- **片語:** {items[i].strip()}\n"
                content += f"  - **定義:** {items[i+1].strip()}\n"
                content += f"  - **例句:** {items[i+2].strip()}\n"
                content += f"    - (翻譯): {items[i+3].strip()}\n"
        content += "\n"
        
    return content

def main():
    """主程式：讀取檔案、分析單字、為每個單字寫入獨立的 .md 檔案"""
    # 建立存放結果的資料夾 (如果不存在)
    os.makedirs(OUTPUT_DIRECTORY_NAME, exist_ok=True)

    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f_in:
            words = [line.strip() for line in f_in if line.strip()]
    except FileNotFoundError:
        print(f"錯誤：找不到輸入檔案 '{INPUT_FILENAME}'。請確認檔案與程式放在同一個資料夾。")
        return

    print(f"找到 {len(words)} 個單字，即將開始分析並存入 '{OUTPUT_DIRECTORY_NAME}' 資料夾...")

    for word in words:
        analysis_text = analyze_word(word)
        if analysis_text:
            parts = analysis_text.split('||')
            if len(parts) >= 7:
                # 將解析結果格式化為 Markdown
                markdown_content = format_as_markdown(word, [p.strip() for p in parts])
                
                # 設定每個單字的檔案路徑與名稱
                file_path = os.path.join(OUTPUT_DIRECTORY_NAME, f"{word}.md")
                
                # 寫入檔案
                try:
                    with open(file_path, 'w', encoding='utf-8') as f_out:
                        f_out.write(markdown_content)
                    print(f" -> 已儲存至 {file_path}")
                except Exception as e:
                    print(f"寫入檔案 '{file_path}' 時發生錯誤: {e}")
            else:
                print(f" -> 單字 '{word}' 的分析結果格式不符，已跳過。")
        else:
            print(f" -> 單字 '{word}' 分析失敗，已跳過。")

    print(f"\n全部分析完成！所有檔案皆已儲存於 '{OUTPUT_DIRECTORY_NAME}' 資料夾中。")

if __name__ == "__main__":
    main()
